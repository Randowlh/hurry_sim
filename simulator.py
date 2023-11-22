from queue import Queue
import distant_tools
from astropy import units as u
import math
import numpy as np
def efficient_lost_packets(n, a):
    """
    Estimate the number of lost packets using binomial distribution.
    
    Args:
    - n (int): total number of packets
    - a (float): probability of losing a packet
    
    Returns:
    - int: number of lost packets
    """
    return np.random.binomial(n, a)

def send_packet_sat_to_gs(satellite_from,gs_to,packet_drop_rate,epoch,now):
  light_speed_m_per_ns=299792458*0.000000001
  distance_m=distant_tools.distance_m_ground_station_to_satellite(gs_to,satellite_from,str(epoch),str(now))
  delay_ns=distance_m/light_speed_m_per_ns
  # packet_drop_rate=0.01
  # if random.random()>packet_drop_rate:
  return delay_ns
  # else: 
    # return None
  
def send_packet_sat_to_sat(satellite_from,satellite_to,packet_drop_rate,epoch,now):
  light_speed_m_per_ns=299792458*0.000000001
  distance_m=distant_tools.distance_m_between_satellites(satellite_from,satellite_to,str(epoch),str(now))
  delay_ns=distance_m/light_speed_m_per_ns
  # if random.random()>packet_drop_rate:
  return delay_ns
  # else: 
    # return None

def get_size(satellite_queue):
  return sum(satellite_queue.values())

def send(key,
         count,
         sat_id_from,
         sat_id_to,
         epoch,
         now,
         num_satellite,
         current_loop_id,
         satellite_queue,ground_station_queue,packet_droped_table,satellites,ground_stations,isl_packet_drop_rate,gsl_packet_drop_rate,time_step):
  delay=None
  if sat_id_to<num_satellite:
    # return
    delay=send_packet_sat_to_sat(satellites[sat_id_from],satellites[sat_id_to],isl_packet_drop_rate,epoch,now)
    if delay!=None:
      # delay+=time_step*0.1
      loss_packet_num=efficient_lost_packets(count,isl_packet_drop_rate)
      packet_droped_table[math.ceil(key/time_step)]+=loss_packet_num
      # try:
      satellite_queue[current_loop_id+math.ceil(delay/time_step)][sat_id_to][key]=satellite_queue[current_loop_id+math.ceil(delay/time_step)][sat_id_to].get(key,0)+count-loss_packet_num
      # except:
        
      #   print(len(satellite_queue[current_loop_id+math.ceil(delay/time_step)][sat_id_to]))
      #   print("satellite_queue",current_loop_id+math.ceil(delay/time_step),sat_id_to,key)
    else:
      packet_droped_table[math.ceil(key/time_step)]+=count
  else:
    delay=send_packet_sat_to_gs(satellites[sat_id_from],ground_stations[sat_id_to-num_satellite],gsl_packet_drop_rate,epoch,now)
    if delay!=None:
      # delay+=time_step*1.1
      loss_packet_num=efficient_lost_packets(count,gsl_packet_drop_rate)
      packet_droped_table[math.ceil(key/time_step)]+=loss_packet_num
      ground_station_queue[current_loop_id+math.ceil(delay/time_step)][sat_id_to-num_satellite][key]=ground_station_queue[current_loop_id+math.ceil(delay/time_step)][sat_id_to-num_satellite].get(key,0)+count-loss_packet_num
    else:
      packet_droped_table[math.ceil(key/time_step)]+=count
    
  
def simulator(
      satellites,
      ground_stations,
      isl_packet_drop_rate,
      gsl_packet_drop_rate,
      routing_table, #[[limit_time,[[to_id,packet_perstep],[to_id_2,packet_perstep_2]],...]]]
      time_step,
      total_sim_time,
      satellite_generated_packages_per_time_step,
      ground_station_to_cloud_bandwidth,
      gsl_link_bandwidth,
      isl_link_bandwidth,
      epoch,
    ):
  max_gsl_length_m=1260000.0000000000
  max_isl_length_m=5442958.2030362869
  total_time_step=int(total_sim_time/time_step)
  num_satellite=len(satellites)
  # print("num_satellite",num_satellite)
  num_ground_station=len(ground_stations)
  satellite_queue=[]
  data_center_queue=[]
  ground_station_queue=[]
  satellite_store_queue=[]
  ground_station_store_queue=[]
  #统计信息
  packet_droped_table=[]
  latency_table=[]
  throughput_table=[]
  satellite_queue_len=[]
  ground_station_queue_len=[]
  # 初始化时隙队列
  for i in range(0, total_time_step+10):
    data_center_queue.append({})
    packet_droped_table.append(0)
    latency_table.append([0,0])
    throughput_table.append(0)
    ground_station_queue_len.append(0)
  
  for i in range(0, total_time_step+10):
      satellite_queue.append([])

      for j in range(0, num_satellite):
          satellite_queue[i].append({})
          
  for i in range(0, total_time_step+10):
      ground_station_queue.append([])
      for j in range(0, num_ground_station):
          ground_station_queue[i].append({})
          
  # 初始化存储队列
  
  for i in range(0, num_satellite+10):
      satellite_queue_len.append([])
      satellite_store_queue.append({})
  for i in range(0, num_ground_station):
      ground_station_store_queue.append({})
  
  #####################################
  #             开始模拟               #
  #####################################
  current_routing_table_id=0
  current_loop_id=0
  for time_since_epoch in range(0,total_sim_time,time_step):
    print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time))
    now=time_since_epoch*u.ns+epoch
    # 计算当前模拟时间
    for satellite_id in range(0,num_satellite):
      satellite_store_queue[satellite_id][time_since_epoch]=satellite_store_queue[satellite_id].get(time_since_epoch,0)+satellite_generated_packages_per_time_step
      # 生成数据包
    if routing_table[current_routing_table_id][0]<now:
      current_routing_table_id+=1
    for satellite_id in range(0,num_satellite): 
      if len(satellite_store_queue[satellite_id])==0:
        continue
      # print("here",satellite_id,current_loop_id)
      Queue_size=get_size(satellite_store_queue[satellite_id])
      satellite_queue_len[satellite_id].append(Queue_size)
      # print("current route id",current_routing_table_id)
      if routing_table[current_routing_table_id][satellite_id+1]!=[]:
        # print("here have routing table")
        #计算传输数据比例
        # print("satellite_id",satellite_id)
        # Queue_size=get_size(satellite_queue[current_loop_id][satellite_id])
        # satellite_queue_len[current_loop_id]+=Queue_size
        total_out_packets=0
        for i in routing_table[current_routing_table_id][satellite_id+1]:
          total_out_packets+=i[1]
        out_percent=min(1,Queue_size/total_out_packets)
        for i in routing_table[current_routing_table_id][satellite_id+1]:
          # 遍历转发表并转发
          out_count=math.floor(i[1]*out_percent)
          if(i[0]<num_satellite):
            out_count=min(out_count,isl_link_bandwidth)
          else:
            out_count=min(out_count,gsl_link_bandwidth)
          # print("out_count",out_count)
          for key in list(satellite_store_queue[satellite_id].keys()):
            if out_count==0:
              break
            if satellite_store_queue[satellite_id][key]<=out_count:
              count=satellite_store_queue[satellite_id][key]
              del satellite_store_queue[satellite_id][key]
              out_count-=count
              send(key,count,satellite_id,i[0],epoch,now,num_satellite,current_loop_id,satellite_queue,ground_station_queue,packet_droped_table,satellites,ground_stations,isl_packet_drop_rate,gsl_packet_drop_rate,time_step)
            else:
              count=out_count
              satellite_store_queue[satellite_id][key]-=out_count
              out_count=0
              send(key,count,satellite_id,i[0],epoch,now,num_satellite,current_loop_id,satellite_queue,ground_station_queue,packet_droped_table,satellites,ground_stations,isl_packet_drop_rate,gsl_packet_drop_rate,time_step)
      ########################
      # 卫星保存数据到下一个时刻
      
      for key in list(satellite_queue[current_loop_id+1][satellite_id].keys()):
        satellite_store_queue[satellite_id][key]=satellite_store_queue[satellite_id].get(key,0)+satellite_queue[current_loop_id+1][satellite_id][key]
      
      #########################

    for ground_station_id in range(0,num_ground_station):
      
      Queue_size=get_size(ground_station_store_queue[ground_station_id])
      
      ground_station_queue_len[current_loop_id]+=Queue_size

      total_out_packets=ground_station_to_cloud_bandwidth[ground_station_id]
      
      for key in list(ground_station_store_queue[ground_station_id].keys()):
        if total_out_packets==0:
          break
        if ground_station_store_queue[ground_station_id][key]<=total_out_packets:
          packet=ground_station_store_queue[ground_station_id][key]
          del ground_station_store_queue[ground_station_id][key]
          total_out_packets-=packet
          data_center_queue[current_loop_id+1][key]=data_center_queue[current_loop_id+1].get(key,0)+packet
        else :
          packet=total_out_packets
          ground_station_store_queue[ground_station_id][key]-=total_out_packets
          total_out_packets=0
          data_center_queue[current_loop_id+1][key]=data_center_queue[current_loop_id+1].get(key,0)+packet
      
      for key in list(ground_station_queue[current_loop_id+1][ground_station_id].keys()):
        ground_station_store_queue[ground_station_id][key]=ground_station_store_queue[ground_station_id].get(key,0)+ground_station_queue[current_loop_id+1][ground_station_id][key]
            
    for key in  list(data_center_queue[current_loop_id].keys()):
      throughput_table[current_loop_id]+=data_center_queue[current_loop_id][key]
      latency_table[current_loop_id][0]+=(time_since_epoch-key)*data_center_queue[current_loop_id][key]
      latency_table[current_loop_id][1]+=data_center_queue[current_loop_id][key]
      del data_center_queue[current_loop_id][key]
    a=satellite_queue[current_loop_id]
    satellite_queue[current_loop_id]=[]
    del a
    a=ground_station_queue[current_loop_id]
    ground_station_queue[current_loop_id]=[]
    del a
    current_loop_id+=1
  latency=[]
  for i in range(0,len(latency_table)):
    if(latency_table[i][1]==0):
      latency.append(0)
    else:
      latency.append(latency_table[i][0]/latency_table[i][1])
  # for i in range(len(satellite_queue)):
  #   print("satellite_queue",i,len(satellite_queue[i]))

  return throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len
    
if __name__ == '__main__':
  pass
  # test here