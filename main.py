from datetime import datetime
import ephem
import multiprocessing
from astropy.time import Time
from astropy import units as u
from read import read_tle
from read import read_ground_stations_extended
from read import read_isls
import distant_tools
import networkx as nx
import matplotlib.pyplot as plt
import random
import sim_baseline
import sim_baseline_with_isl
import sim_with_umbra
import sim_with_max_flow_isl
satellite_generated_packages_per_time_step = 43
ground_station_handle_packages_per_time_step = []
ground_station_max_transmit_packets_per_time_step = []
ground_station_max_cap = 310000
isl_max_cap = 40
throughput_table = []
throughput_table_with_isl = []
max_gsl_length_m = 1260000.0000000000
max_isl_length_m = 5442958.2030362869
m_ground_stations = []
throughput_table_with_umbra=[]
m_satellite = []
isl_packet_drop_rate = 0.01
gsl_packet_drop_rate = 0.12
satellite_num = 0
ground_station_num = 0
m_epoch = None
edges = []
num_orbits = 0
m_satellite_queue = []
m_ground_station_queue = []
m_ground_station_cap = []
num_satellites_per_orbit = 0
total_sim_time_ns = 2000000000000 # 3s
sim_time_step_ns = 10000000 # 1ms
inf = 99999999999999

def generate_bandwidth(total, num):
    """
    Generate a list of bandwidths for each ground station, such that the total bandwidth is as close to the total as possible

    :param total: Total bandwidth
    :param num:   Number of ground stations

    :return: List of bandwidths
    """
    bandwidths = []
    random_nums = sorted(random.sample(range(1, total), num-1))
    random_nums.append(total)
    for i in range(0, num):
        if i == 0:
            bandwidths.append(random_nums[i])
        else:
            bandwidths.append(random_nums[i] - random_nums[i-1])
    # print(num)
    # print(bandwidths)
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
    total_data_rate=int(len(m_satellite)*satellite_generated_packages_per_time_step)
    total_handle_rate=int(total_data_rate*1.2)
    ground_station_handle_packages_per_time_step=generate_bandwidth(total_handle_rate,len(m_ground_stations))
    ground_station_max_transmit_packets_per_time_step=generate_bandwidth(total_data_rate,len(m_ground_stations))
    for i in range(0, len(m_satellite)):
        m_satellite_queue.append(0)
    for i in range(0, len(m_ground_stations)):
        m_ground_station_queue.append(0)
    for i in range(0, len(m_ground_stations)):
        m_ground_station_cap.append(ground_station_max_cap)
        
        

#############################################################
def store_throughput_table():
    global throughput_table,throughput_table_with_isl,throughput_table_with_umbra
  
    
    
            
            
#########################################################################33
#################################################################



def run_baseline():
    global throughput_table
    throughput_table = sim_baseline.sim_baseline(total_sim_time_ns,
                                                 sim_time_step_ns,
                                                 m_satellite,
                                                 m_ground_stations,
                                                 m_epoch,
                                                 satellite_generated_packages_per_time_step,
                                                 max_gsl_length_m,
                                                 ground_station_max_transmit_packets_per_time_step,
                                                 ground_station_max_cap,
                                                 ground_station_handle_packages_per_time_step)
    # print("sim_baseline complete")
    # print(throughput_table)
    with open("throughput.txt", 'w') as f:
        for i in throughput_table:
            f.write(str(i)+"\n")

def run_with_isl():
    global throughput_table_with_isl
    throughput_table_with_isl = sim_baseline_with_isl.sim_with_isl(m_satellite,
                                                                   m_ground_stations,
                                                                   edges,
                                                                   total_sim_time_ns,
                                                                   sim_time_step_ns,
                                                                   m_epoch,
                                                                   satellite_generated_packages_per_time_step,
                                                                   ground_station_max_transmit_packets_per_time_step,
                                                                   max_gsl_length_m,
                                                                   ground_station_max_cap,
                                                                   ground_station_handle_packages_per_time_step,
                                                                   isl_max_cap)
    # print("sim_with_isl complete")
    with open("throughput_with_isl.txt", 'w') as f:
        for i in throughput_table_with_isl:
            f.write(str(i)+"\n")

def run_with_umbra():
    global throughput_table_with_umbra
    throughput_table_with_umbra = sim_with_umbra.sim_with_umbra(total_sim_time_ns,
                                                                 sim_time_step_ns,
                                                                 m_satellite,
                                                                 m_ground_stations,
                                                                 m_epoch,
                                                                 satellite_generated_packages_per_time_step,
                                                                 ground_station_handle_packages_per_time_step,
                                                                 ground_station_max_cap,
                                                                 ground_station_max_transmit_packets_per_time_step)
    # print("sim_with_umbra complete")
    # print(throughput_table_with_umbra)
    with open("throughput_with_umbra.txt", 'w') as f:
        for i in throughput_table_with_umbra:
            f.write(str(i)+"\n")
            
def run_with_max_flow_isl():
    global throughput_table_with_max_flow_isl
    throughput_table_with_max_flow_isl = sim_with_max_flow_isl.sim_with_max_flow_isl(total_sim_time_ns,
                                                                 sim_time_step_ns,
                                                                 m_satellite,
                                                                 m_ground_stations,
                                                                 m_epoch,
                                                                 satellite_generated_packages_per_time_step,
                                                                 ground_station_handle_packages_per_time_step,
                                                                 ground_station_max_cap,
                                                                 ground_station_max_transmit_packets_per_time_step,
                                                                 edges,
                                                                 isl_max_cap
                                                                 )
    # print("sim_with_umbra complete")
    # print(throughput_table_with_umbra)
    with open("throughput_with_max_flow_isl.txt", 'w') as f:
        for i in throughput_table_with_max_flow_isl:
            f.write(str(i)+"\n")
##################################################################

##################################################################

def main():
    # Initialize multiprocessing processes
    p1 = multiprocessing.Process(target=run_baseline)
    p2 = multiprocessing.Process(target=run_with_isl)
    p3 = multiprocessing.Process(target=run_with_umbra)
    p4 = multiprocessing.Process(target=run_with_max_flow_isl)

    # Start processes
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    # Wait for processes to finish
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    global throughput_table,throughput_table_with_isl,throughput_table_with_umbra
    # print("baseline")   
    # print(throughput_table)
    # print("with isl")
    # print(throughput_table_with_isl)
    # print("with umbra")
    # print(throughput_table_with_umbra)
    # Store results and other post-processing
    store_throughput_table()

if __name__ == "__main__":
    init()
    main()