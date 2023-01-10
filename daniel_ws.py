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

    #assign addr for filter and ifmap
    filt_addr =[]
    ifmap_base_addr =[]
    ifmap_offset = []
    
    for f in range(num_filt):
        filt_addr.append(f*r2c + filt_base)
    
    hc = ifmap_w * num_channels
    for i in range(e2):
        addr = (i%E_w)*num_channels*strides + math.floor(i/E_w)*hc*strides
        ifmap_base_addr.append(addr)
    
    for i in range(r2c):
        addr = math.floor(i/E_w)*hc*strides + (i%E_w)*strides
        ifmap_offset.append(addr)

    prefill = ""
    num_rows = dimension_rows
    num_cols = dimension_cols

    #each block addr
    h_fold = 0
    v_fold = 0


    #prefill weights
    for r in range(num_rows):
        prefill += str(cycles)+", "
        cycles += 1
        for k in range(num_rows):
            prefill += ", "
        for c in range(num_cols):
            prefill += str(filt_addr[c]+r)+", "
        prefill += "\n"
    
    trace = prefill
    #stream ifmap windows
    for i in range(e2):
        trace += str(cycles)+", "
        cycles += 1
        ifmap_buf =[]
        for r in range(num_rows,0,-1):
            addr = ifmap_base_addr[i]+ifmap_offset[r-1]
            trace += str(addr)+", "
        for c in range(num_cols):
            trace += ", "
        trace += "\n"
    
    #그냥 2차원에 쫙 weight 저장해버리면? PE가 옮겨다니는 거임
    h_fold += 1
    #now, the needed_row is 2, column same
    #by doing this, we can finish 5 output channels
    
    

    print(trace)
            

                
                




if __name__ == "__main__":
   sram_traffic(
       dimension_rows = 6,
       dimension_cols = 5,
       ifmap_h = 5, ifmap_w = 5,
       filt_h = 2, filt_w = 2,
       num_channels = 2, strides = 1,
       num_filt = 9
   )
