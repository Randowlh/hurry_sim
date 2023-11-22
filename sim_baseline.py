
from astropy.time import Time
from astropy import units as u
import distant_tools
import caculation_brand
#############################################################
from multiprocessing import Process

def generate_baseline(total_sim_time_ns,
        sim_time_step_ns,
        satellites,
        ground_stations,
        epoch,
        max_gsl_length_m,
        # gsl_max_cap,# 星地链路最大带宽,默认为1.2倍星地链路
        gsl_base_link_cap,#list 每个地面站星地链路大小      
        ):  
    satellite_queue=[]
    ground_station_queue=[]
    for i in range(0, len(satellites)):
        satellite_queue.append(0)
    for i in range(0, len(ground_stations)):
        ground_station_queue.append(0)
    routing_table=[]
    ground_station_flag=[]
    for i in range(0, len(ground_stations)):
        ground_station_flag.append(0)
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        print("baseline generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
            
        now=time_since_epoch*u.ns+epoch
        
        routing_table_now=[now]

        # 计算当前模拟时间
        # satellite_id=0
        #当前卫星id
        #多进程处理
        for satellite_id in range(len(satellites)):
            
            routing_table_satellite=[]
            max_dis=max_gsl_length_m
            closest_groundstation=None
            for groundstation in ground_stations:
                dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellites[satellite_id],str(epoch),str(now))
                if dis<max_dis:
                    max_dis=dis
                    closest_groundstation=groundstation
            if closest_groundstation!=None and ground_station_flag[closest_groundstation["gid"]]==0:
                # print("satellite_id",satellite_id,"closest_groundstation",closest_groundstation["gid"])
                gsl_link_cap=caculation_brand.calculate_rate(gsl_base_link_cap[closest_groundstation["gid"]],satellites[satellite_id],closest_groundstation,epoch,now)
                routing_table_satellite.append([closest_groundstation["gid"]+len(satellites),gsl_link_cap]) 
                ground_station_flag[closest_groundstation["gid"]]=1
            routing_table_now.append(routing_table_satellite)
        # print("generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        routing_table.append(routing_table_now)
    print("sim_baseline generating complete")
    # print("routing_table",routing_table)
    print(routing_table)
    return routing_table
