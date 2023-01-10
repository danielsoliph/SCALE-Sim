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
    
    for c in range(num_filt):
        addr = c* r2c +filt_base
        filt_addr.append(addr)

    hc = ifmap_w * num_channels
    ofmap_w = E_w
    ofmap_h = E_h

    for ofmap_px in range(e2):
        addr = (ofmap_px / ofmap_w) *strides*hc + (ofmap_px % ofmap_w)*strides
        ifmap_base_addr.append(addr)


    #assuming no fold
    cycles_filt = gen_filter_trace(
                    cycle = cycles,
                    dim_rows = dimension_rows,
                    dim_col = dimension_cols,
                    filt_h = filt_h,
                    filt_w = filt_w,
                    num_filt = num_filt,
                    num_channels = num_channels,
                    filt_addr = filt_addr,
                    sram_read_trace_file = sram_read_trace_file
                    )

    cycles_ifmap = gen_ifmap_trace(
                    cycle = cycles_filt,
                    dim_rows = dimension_rows,
                    dim_cols = dimension_cols,
                    ifmap_h = ifmap_h,
                    ifmap_w = ifmap_w,
                    filt_h = filt_h,
                    filt_w = filt_w,
                    num_channels = num_channels,
                    strides = strides,
                    sram_read_trace_file = sram_read_trace_file
                    )
    cycles_ofmap = gen_ofmap_trace(
                    cycle = cycles_filt,
                    dim_rows = dimension_rows,
                    dim_cols = dimension_cols,
                    ofmap_base = ofmap_base,
                    num_filt = num_filt,
                    sram_write_trace_file = sram_write_trace_file
                    )




        

    
def gen_filter_trace(
        cycle =0,
        dim_rows=4;
        dim_cols=4,
        filt_h =3, filt_w =3,
        num_channels =3,
        num_filt =8,
        filt_addr = [],
        sram_read_trace_file = "sram_read.csv"
    ):
    outfile = open(sram_read_trace_file,'w')
    ifmap_data=""
    for r in range(dim_rows):
        ifmap_data += ", "

    r2c = filt_h * filt_w * num_channels
    for r in range(r2c):
        data_in = str(cycle) + ", "+ifmap_data
        cycle += 1
        for c in range(num_filt):
            data_in += str(filt_addr[c]) + ", "
            filt_addr[c] += 1
        if num_filt < dim_cols:
            for k in range(c,num_cols):
                data_in += ", "
        data_in += "\n"
        outfile.write(data_in)
    outfile.close()
    return cycle
    
def gen_ifmap_trace(
        cycle = 0,
        dim_rows = 4, dim_cols =4,
        ifmap_h = 7, ifmap_w = 7,
        filt_h = 2, filt_w = 2,
        num_channels = 3,
        strides = 1,
        sram_read_trace_file = "sram_read.csv"
):
    outfile = open(sram_read_trace_file,'w')
    filt_data =""

    
    
def gen_ofmap_trace:
    
    




if __name__ == "__main__":
   sram_traffic(
       dimension_rows = 8,
       dimension_cols = 4,
       ifmap_h = 7, ifmap_w = 7,
       filt_h = 2, filt_w = 2,
       num_channels = 1, strides = 1,
       num_filt = 7
   )
