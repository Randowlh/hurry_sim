from datetime import datetime
import ephem
import sys
import os
import multiprocessing
from astropy.time import Time
from astropy import units as u
from read import read_tle
from read import read_ground_stations_extended
from read import read_isls
import distant_tools
import networkx as nx
import matplotlib.pyplot as plt
import sim_baseline
import sim_baseline_with_isl
import sim_with_umbra
import sim_with_max_flow_isl
import sim_with_coDld
import sim_with_hurry
import sim_with_cost_flow
import simulator
import sim_with_test
import sim_with_coDld_motify
satellite_generated_packages_per_time_step = 4 # 400 mbps
ground_station_handle_packages_per_time_step=999999999


throughput_table = []
throughput_table_with_isl = []
max_gsl_length_m = 1260000.0000000000
max_isl_length_m = 5442958.2030362869
total_generating_time=0
m_ground_stations = []
throughput_table_with_umbra=[]
m_satellite = []
isl_packet_drop_rate = 0
gsl_packet_drop_rate = 0
satellite_num = 0
ground_station_num = 0
m_epoch = None
edges = []
num_orbits = 0
m_satellite_queue = []
m_ground_station_queue = []
m_ground_station_cap = []
num_satellites_per_orbit = 0
total_generating_time = 0
inf = 99999999999999
full_path_str=""
if(len(sys.argv)<=1):
    print("Usage: python main.py [total_sim_time_ms] [sim_time_step_ms][ total_generating_time] [satellite_generated_packages_per_time_step] [ground_station_max_transmit_packets_per_time_step] [isl_max_cap] [sim name]")
    exit(1)
total_sim_time_ns=int(sys.argv[1])*1000000
sim_time_step_ns=int(sys.argv[2])*1000000
total_generating_time=int(sys.argv[3])*1000000
satellite_generated_packages_per_time_step=int(sys.argv[4])
ground_station_max_transmit_packets_per_time_step=int(sys.argv[5])
ground_station_max_cap=ground_station_max_transmit_packets_per_time_step
isl_max_cap=int(sys.argv[6])
sim_name=sys.argv[7]
folder_name = sim_name+"_sat_"+str(satellite_generated_packages_per_time_step)+"_gsl_"+str(ground_station_max_transmit_packets_per_time_step)+"_sim_time_"+str(total_sim_time_ns//1000000)+"_sim_step_"+str(sim_time_step_ns//1000000)
father_path = "gen_data"

full_path = os.path.join(father_path, folder_name)
os.makedirs(full_path, exist_ok=True)
os.makedirs(full_path+"/"+"baseline_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_isl_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_umbra_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_flow_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_coDld_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_coDld_motify_queue", exist_ok=True)

os.makedirs(full_path+"/"+"with_test_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_hurry_queue", exist_ok=True)
os.makedirs(full_path+"/"+"with_cost_flow_queue", exist_ok=True)
full_path_str=full_path+"/"
def generate_bandwidth(total, num):
    """
    Generate a list of bandwidths for each ground station, such that the total bandwidth is as close to the total as possible

    :param total: Total bandwidth
    :param num:   Number of ground stations

    :return: List of bandwidths
    """
    bandwidths = []
    for i in range(0, num):
        bandwidths.append(total//num)
            # random_nums = sorted(random.sample(range(1, total), num-1))
            # random_nums.append(total)
            # for i in range(0, num):
            #     if i == 0:
            #         bandwidths.append(random_nums[i])
            #     else:
            #         bandwidths.append(random_nums[i] - random_nums[i-1])
            # # print(num)
            # # print(bandwidths)
    return bandwidths
    
#############################################
def init():
    global inf,m_epoch, m_satellite, m_ground_stations, num_orbits, num_satellites_per_orbit, isl_file_name, m_satellite_queue, m_ground_station_queue,satellite_num,edges,ground_station_handle_packages_per_time_step,ground_station_max_transmit_packets_per_time_step
    current_time = datetime.now()
    print("time=" + str(current_time))
    tle_file_name = "tles.txt"
    isl_file_name = "isls.txt"
    ground_stations_file_name = "ground_stations.txt"
    tles= read_tle(tle_file_name)
    num_orbits=tles["n_orbits"]
    num_satellites_per_orbit=tles["n_sats_per_orbit"]
    m_epoch=tles["epoch"]
    m_satellite=tles["satellites"]
    edges=read_isls(isl_file_name, len(m_satellite))
    m_ground_stations = read_ground_stations_extended(ground_stations_file_name)
    ground_station_handle_packages_per_time_step=generate_bandwidth(ground_station_handle_packages_per_time_step*len(m_ground_stations),len(m_ground_stations))
    ground_station_max_transmit_packets_per_time_step=generate_bandwidth(ground_station_max_transmit_packets_per_time_step*len(m_ground_stations),len(m_ground_stations))
    for i in range(0, len(m_satellite)):
        m_satellite_queue.append(0)
    for i in range(0, len(m_ground_stations)):
        m_ground_station_queue.append(0)
    for i in range(0, len(m_ground_stations)):
        m_ground_station_cap.append(ground_station_max_cap)
        
        

#############################################################
def store_throughput_table():
    global throughput_table,throughput_table_with_isl,throughput_table_with_umbra
  
    
    
            
            
#########################################################################
#################################################################



def run_baseline():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m
    routing_table = sim_baseline.generate_baseline(total_sim_time_ns,
                                                 sim_time_step_ns,
                                                 m_satellite.copy(),
                                                 m_ground_stations.copy(),
                                                 m_epoch,
                                                 max_gsl_length_m,
                                                 ground_station_max_transmit_packets_per_time_step.copy(),
                                                 )
    

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,
                                                                                                                  total_generating_time
                                                                                                                  
                                                                                                                  )
    with open(full_path_str+"throughput.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"baseline_queue/"+"SAT"+str(i)+"satellite_queue_len_baseline.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    # print("simulator complete")   


def run_with_test():
    global m_satellite,m_ground_stations,edges,total_sim_time_ns,sim_time_step_ns,m_epoch,ground_station_max_transmit_packets_per_time_step,max_gsl_length_m,isl_max_cap
    routing_table = sim_with_test.generate_with_test(m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            edges.copy(),
                                                            total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_epoch,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            isl_max_cap)

    
    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,
                                                                                                                  total_generating_time
                                                                                                                  )
    with open(full_path_str+"throughput_with_test.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_test.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_test.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_test_queue/"+"SAT"+str(i)+"satellite_queue_len_with_test.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len_with_test.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")       


def run_with_isl():
    global m_satellite,m_ground_stations,edges,total_sim_time_ns,sim_time_step_ns,m_epoch,ground_station_max_transmit_packets_per_time_step,max_gsl_length_m,isl_max_cap
    routing_table = sim_baseline_with_isl.generate_with_isl(m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            edges.copy(),
                                                            total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_epoch,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            isl_max_cap)

    
    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,
                                                                                                                    total_generating_time
                                                                                                                  )
    with open(full_path_str+"throughput_with_isl.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_isl.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_isl.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_isl_queue/"+"SAT"+str(i)+"satellite_queue_len_with_isl.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len_with_isl.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")       

def run_with_umbra():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m
    routing_table = sim_with_umbra.sim_with_umbra(total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            
                                                            m_epoch,
                                                            satellite_generated_packages_per_time_step,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            
                                                            ground_station_handle_packages_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            total_generating_time,
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_with_umbra.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_umbra.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_umbra.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_umbra_queue/"+"SAT"+str(i)+"satellite_queue_len_with_umbra.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len_with_umbra.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   
            
def run_with_max_flow_isl():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m,edges,isl_max_cap
    routing_table = sim_with_max_flow_isl.sim_with_maxflow(total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            
                                                            m_epoch,
                                                            satellite_generated_packages_per_time_step,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            
                                                            ground_station_handle_packages_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            edges.copy(),
                                                            isl_max_cap,
                                                            total_generating_time
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_with_flow.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_flow.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_flow.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_flow_queue/"+"SAT"+str(i)+"satellite_queue_len_with_flow.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")

    with open(full_path_str+"ground_station_queue_len_with_flow.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   
    
def run_with_cost_flow():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m,edges,isl_max_cap
    routing_table = sim_with_cost_flow.sim_with_cost_flow(total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            
                                                            m_epoch,
                                                            satellite_generated_packages_per_time_step,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            
                                                            ground_station_handle_packages_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            edges.copy(),
                                                            isl_max_cap,
                                                            total_generating_time
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_with_cost_flow.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_cost_flow.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_cost_flow.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_cost_flow_queue/"+"SAT"+str(i)+"satellite_queue_len_with_cost_flow.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")

    with open(full_path_str+"ground_station_queue_len_with_cost_flow.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   
    
def run_with_hurry():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m,edges,isl_max_cap
    routing_table = sim_with_hurry.sim_with_hurry(total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            
                                                            m_epoch,
                                                            satellite_generated_packages_per_time_step,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            
                                                            ground_station_handle_packages_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            edges.copy(),
                                                            isl_max_cap,
                                                            total_generating_time
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_with_hurry.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_with_hurry.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"packet_droped_table_with_hurry.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_hurry_queue/"+"SAT"+str(i)+"satellite_queue_len_with_hurry.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")

    with open(full_path_str+"ground_station_queue_len_with_hurry.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   

def run_with_coDld():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m,edges,isl_max_cap
    routing_table = sim_with_coDld.generate_with_coDld(
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            edges.copy(),
                                                            total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_epoch,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            isl_max_cap,
                                                            satellite_generated_packages_per_time_step,
                                                            total_generating_time
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_coDld.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_coDld.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"drop_coDld.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_coDld_queue/"+"SAT"+str(i)+"satellite_queue_len_with_coDld.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len_with_coDld.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   
    
def run_with_coDld_motify():
    global total_sim_time_ns,sim_time_step_ns,m_satellite,m_ground_stations,m_epoch,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step,max_gsl_length_m,edges,isl_max_cap
    routing_table = sim_with_coDld_motify.generate_with_coDld(
                                                            m_satellite.copy(),
                                                            m_ground_stations.copy(),
                                                            edges.copy(),
                                                            total_sim_time_ns,
                                                            sim_time_step_ns,
                                                            m_epoch,
                                                            ground_station_max_transmit_packets_per_time_step.copy(),
                                                            max_gsl_length_m,
                                                            isl_max_cap,
                                                            satellite_generated_packages_per_time_step,
                                                            total_generating_time
                                                            )

    # print("sim_baseline complete")
    # print(routing_table)
    # return
    # print(throughput_table)
    throughput_table,latency,packet_droped_table,satellite_queue_len,ground_station_queue_len=simulator.simulator(m_satellite.copy(),
                                                                                                                  m_ground_stations.copy(),
                                                                                                                  isl_packet_drop_rate,
                                                                                                                  gsl_packet_drop_rate,
                                                                                                                  routing_table.copy(),
                                                                                                                  sim_time_step_ns,
                                                                                                                  total_sim_time_ns,
                                                                                                                  satellite_generated_packages_per_time_step,
                                                                                                                  ground_station_handle_packages_per_time_step.copy(),
                                                                                                                  ground_station_max_cap,
                                                                                                                  isl_max_cap,
                                                                                                                  m_epoch,total_generating_time)
    with open(full_path_str+"throughput_coDld_motify.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")
    with open(full_path_str+"latency_coDld_motify.txt", 'w') as f:
        for i in latency:
            f.write(str(i)+"\n")
    with open(full_path_str+"drop_coDld_motify.txt", 'w') as f:
        for i in packet_droped_table:
            f.write(str(i)+"\n")
    for i in range(0, len(m_satellite)):
        with open(full_path_str+"with_coDld_motify_queue/"+"SAT"+str(i)+"satellite_queue_len_with_coDld_motify.txt", 'w') as f:
            for j in satellite_queue_len[i]:
                f.write(str(j)+"\n")
    with open(full_path_str+"ground_station_queue_len_with_coDld_motify.txt", 'w') as f:
        for i in ground_station_queue_len:
            f.write(str(i)+"\n")
    print("simulator complete")   
##################################################################

##################################################################

def main():
    # # Initialize multiprocessing processes
    p1 = multiprocessing.Process(target=run_baseline)
    p2 = multiprocessing.Process(target=run_with_isl)
    p3 = multiprocessing.Process(target=run_with_umbra)
    p4 = multiprocessing.Process(target=run_with_max_flow_isl)
    p5 = multiprocessing.Process(target=run_with_coDld)
    p6 = multiprocessing.Process(target=run_with_test)
    p7 = multiprocessing.Process(target=run_with_cost_flow)
    p8 = multiprocessing.Process(target=run_with_hurry)
    p9 = multiprocessing.Process(target=run_with_coDld_motify)
    # Start processes
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p9.start()
    # Wait for processes to finish
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    p9.join()
    # global throughput_table,throughput_table_with_isl,throughput_table_with_umbra
    # print("baseline")   
    # print(throughput_table)
    # print("with isl")
    # print(throughput_table_with_isl)
    # print("with umbra")
    # print(throughput_table_with_umbra)
    # Store results and other post-processing
    # store_throughput_table()

def init_main():
    global total_sim_time_ns,sim_time_step_ns,total_generating_time,satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,isl_max_cap,full_path_str
    init()
    main()
init_main()