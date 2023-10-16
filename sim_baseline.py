
from astropy.time import Time
from astropy import units as u
import distant_tools
#############################################################
from multiprocessing import Process

def sim_baseline(total_sim_time_ns,
        sim_time_step_ns,
        satellites,
        ground_stations,
        epoch,
        satellite_generated_packages_per_time_step,
        max_gsl_length_m,
        # gsl_max_cap,# 星地链路最大带宽,默认为1.2倍星地链路
        ground_station_max_transmit_packets_per_time_step,#list 每个地面站星地链路大小
        ground_station_max_cap,#地面站队列大小
        ground_station_handle_packages_per_time_step,#list地面站到数据中心带宽大小
        ):  
    satellite_queue=[]
    ground_station_queue=[]
    for i in range(0, len(satellites)):
        satellite_queue.append(0)
    for i in range(0, len(ground_stations)):
        ground_station_queue.append(0)
    throughput_table=[]
    processes = []
    ground_station_flag=[]
    for i in range(0, len(ground_stations)):
            ground_station_flag.append(0)
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        # 计算当前模拟时间
        satellite_id=0
        #当前卫星id
        #多进程处理
        for satellite in satellites:
            simulate_satellite(satellite, 
                                satellite_id, 
                                epoch,
                                now, 
                                satellite_queue,
                                ground_stations, 
                                ground_station_flag,
                                ground_station_max_transmit_packets_per_time_step,
                                ground_station_queue,
                                ground_station_max_cap,
                                max_gsl_length_m,
                                satellite_generated_packages_per_time_step)
            satellite_id+=1
        print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        for groundstation in ground_stations:
            pre=ground_station_queue[groundstation["gid"]]
            ground_station_queue[groundstation["gid"]]-=ground_station_handle_packages_per_time_step[groundstation["gid"]]
            ground_station_queue[groundstation["gid"]]=max(0,ground_station_queue[groundstation["gid"]])
            total_throughput+=pre-ground_station_queue[groundstation["gid"]]
        throughput_table.append(total_throughput)
    print("sim_baseline complete")
    return throughput_table

def simulate_satellite(satellite,
                       satellite_id, 
                       epoch,
                       now,
                       satellite_queue, 
                       ground_stations,
                       ground_station_flag,
                       ground_station_max_transmit_packets_per_time_step, 
                       ground_station_queue,
                       ground_station_max_cap,
                       max_gsl_length_m,
                       satellite_generated_packages_per_time_step):
    satellite_queue[satellite_id]+=satellite_generated_packages_per_time_step
    
    max_dis=max_gsl_length_m
    closest_groundstation=None
    
    for groundstation in ground_stations:
        dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellite,str(epoch),str(now))
        if dis<max_dis:
            max_dis=dis
            closest_groundstation=groundstation
    #if there is a ground station in the range
    if closest_groundstation!=None and ground_station_flag[closest_groundstation["gid"]]==0:
        ground_station_flag[closest_groundstation["gid"]]=1
        packet_sented=min(satellite_queue[satellite_id],ground_station_max_transmit_packets_per_time_step[closest_groundstation["gid"]])
        satellite_queue[satellite_id]-=packet_sented
        packet_sented=min(packet_sented,ground_station_max_transmit_packets_per_time_step[closest_groundstation["gid"]])
        ground_station_queue[closest_groundstation["gid"]]+=packet_sented
        
        # ground station over flow
        if(ground_station_queue[closest_groundstation["gid"]]>ground_station_max_cap):
            # print("ground station "+str(closest_groundstation["gid"])+" overflow")
            dis=ground_station_queue[closest_groundstation["gid"]]-ground_station_max_cap
            ground_station_queue[closest_groundstation["gid"]]=ground_station_max_cap
            packet_sented-=dis
        # ground_station_cap[closest_groundstation["gid"]]+=packet_sented
    