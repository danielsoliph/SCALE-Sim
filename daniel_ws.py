import math 
from tqdm import tqdm

neg_inf = -1 * math.pow(2,32)

def sram_traffic(
        dimension_rows=4,
        dimension_cols=4,
        ifmap_h=7, ifmap_w=7,
        filt_h=3, filt_w=3,
        num_channels=3,
        strides=1, num_filt=8,
        ofmap_base=2000000, filt_base=1000000, ifmap_base=0,
        sram_read_trace_file="new_ws_sram_read.csv",
        sram_write_trace_file="new_ws_sram_write.csv"
):

    # Number of logical PEs needed for WS (ideally without mapping)
    # row : R^2C ,col: M
    # each weight is used E^2 times

    # Dimensions of output feature map channel
    E_h = math.floor((ifmap_h - filt_h + strides) / strides)
    E_w = math.floor((ifmap_w - filt_w + strides) / strides)
    
    # Number of pixels in one convolution window
    px_per_conv_window = filt_h * filt_w * num_channels
    r2c = px_per_conv_window
    rc = filt_w * num_channels
    # Total number of ofmap px across all channels
    num_ofmap_px = E_h * E_w * num_filt
    e2  = E_h * E_w
    e2m = num_ofmap_px
    
    # Variables to calculate folds in runtime
    num_h_fold = math.ceil(r2c/dimension_rows)
    num_v_fold = math.ceil(num_filt/dimension_cols)

    #logical PE dimension
    total_rows = r2c
    total_cols = num_filt

    util = 0
    cycles = 0
    write_cycles = 0
    local_cycle =0

    outfile_read = open(sram_read_trace_file,'w')
    outfile_write = open(sram_write_trace_file,'w')
    
    tot = num_v_fold
    pbar = tqdm(total=tot)

    #assign addr for filter and ifmap
    filt_addr =[]
    ifmap_base_addr =[]
    ifmap_offset = []
    ofmap_addr =[]

    for f in range(num_filt):
        addr = f*r2c + filt_base
        filt_addr.append(addr)
    
    hc = ifmap_w * num_channels
    for i in range(e2):
        addr = (i%E_w)*num_channels*strides + math.floor(i/E_w)*hc*strides
        ifmap_base_addr.append(addr)
        addr = i*num_filt + ofmap_base
        ofmap_addr.append(addr)
    
    for i in range(r2c):
        addr = math.floor(i/rc)*hc + (i%rc)
        ifmap_offset.append(addr)
    
    #for i in range(e2):
    #    addr = i * num_filt +ofmap_base
    #    ofmap_addr.append(addr)

    trace = ""
    write_trace = ""
    num_rows = dimension_rows
    num_cols = dimension_cols
    filt_left = num_filt

    trace_list = []
    write_trace_list =[]
    
    #each block addr
    h_fold = 0
    v_fold = 0

    #print("num_v,num_h: "+str(num_v_fold)+", "+str(num_h_fold))
    while( v_fold<num_v_fold):
        #print("v,h: "+str(v_fold) + ", " + str(h_fold))
        filt_row = h_fold*num_rows
        filt_col = v_fold*num_cols
        row_use = min(num_rows,r2c - filt_row)
        col_use = min(num_cols,num_filt - filt_col)
        

        #prefill weights
        for r in range(filt_row,filt_row + row_use):
            trace_list.append(str(cycles))
            trace_list.append(", ")
            cycles += 1
            #for k in range(num_rows):
            #    trace += ", "
            trace_list.append(", " * num_rows)
            for c in range(filt_col,filt_col + col_use):
                trace_list.append(str(filt_addr[c]+r)+", ")
            trace_list.append("\n")

        write_cycles = cycles

        #stream ifmap windows
        for i in range(e2):
            trace_list.append(str(cycles))
            trace_list.append(", ")
            cycles += 1
            #need to arrange the racnge
            for r in range(row_use+filt_row,filt_row,-1):
                addr = ifmap_base_addr[i]+ifmap_offset[r-1]
                trace_list.append(str(addr)+", ")
            #for c in range(num_cols):
            #    trace += ", "
            trace_list.append(", " * num_cols)
            trace_list.append("\n")
        #print(trace) 
    
        #then, wait until the sram_write is done
        write_cycles += col_use + row_use
    
        for o in range(e2):
            write_trace_list.append(str(write_cycles)+", ")
            write_cycles += 1
            for f in range(filt_col,filt_col+col_use):
                write_trace_list.append(str(ofmap_addr[o] + f) +", ")
            write_trace_list.append("\n")
        
        #print(write_trace)

        h_fold += 1
        if(num_h_fold == h_fold):
            v_fold += 1
            pbar.update(1)
            h_fold = 0
            
        
        cycles = write_cycles
    
        #now, the needed_row is 2, column same
        
        #now to take care of v_fold?
        #later...
        
        #util calculation
        this_util = (row_use * col_use)/(num_rows * num_cols)
        util += this_util
        local_cycle += 1
        final_util = (util/local_cycle) * 100
    
    #print(trace)
    #print(write_trace)
    #print(final_util)
    #print(str(cycles-1))
    trace = ''.join(trace_list)
    write_trace = ''.join(write_trace_list)
    outfile_read.write(trace)
    outfile_write.write(write_trace)

    pbar.close()
    outfile_read.close()
    outfile_write.close()

    #by doing this, finished 5 output channels
    #we just need to do the other 3 output channels                
                
    return str(cycles),final_util



if __name__ == "__main__":
   sram_traffic(
       dimension_rows = 12,
       dimension_cols = 5,
       ifmap_h = 5, ifmap_w = 5,
       filt_h = 2, filt_w = 2,
       num_channels = 2, strides = 1,
       num_filt = 9
   )
