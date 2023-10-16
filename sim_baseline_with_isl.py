import networkx as nx
import astropy.units as u
import distant_tools
def sim_with_isl(satellites,
                 ground_stations,
                 edges,
                 total_sim_time_ns,
                 sim_time_step_ns,
                 epoch,
                 satellite_generated_packages_per_time_step,
                 ground_station_max_transmit_packets_per_time_step,
                 max_gsl_length_m,
                 ground_station_max_cap,
                 ground_station_handle_packages_per_time_step,
                 isl_max_cap
                 ):
    #init queue
    inf = 99999999999999
    m_satellite_queue=[]
    ground_station_flag=[]
    throughput_table_with_isl=[]
    m_ground_station_queue=[]
    for i in range(0, len(satellites)):
        m_satellite_queue.append(0)
    for i in range(0, len(ground_stations)):
        m_ground_station_queue.append(0)
        ground_station_flag.append(0)
    # Create an empty graph
    G = nx.Graph()
    # add node to the graph
    for i in range(0, len(satellites)):
        G.add_node(i)
    # edges : [[1,2],[3,4]] : 1-2, 3-4
    for edge in edges:
        G.add_edge(edge[0], edge[1])
        G.add_edge(edge[1], edge[0]) #need correct
        
    dist_sat_gragh=nx.floyd_warshall_numpy(G)
    
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        satellite_choose=[] 
        for groundstation in ground_stations:
            #finding the closest satellite
            max_dis=inf
            closest_satellite=-1
            satellite_id=0
            for satellite in satellites:
                dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellite,str(epoch),str(now))
                if dis<max_dis:
                    max_dis=dis
                    closest_satellite=satellite_id
                satellite_id+=1
            satellite_choose.append(closest_satellite)
        for satellite_id in range(0,len(satellites)):
            m_satellite_queue[satellite_id]+=satellite_generated_packages_per_time_step
            ########################################
            max_dis=max_gsl_length_m
            closest_groundstation=None
            for groundstation in ground_stations:
                dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellite,str(epoch),str(now))
                if dis<max_dis:
                    max_dis=dis
                    closest_groundstation=groundstation
            if closest_groundstation!=None and ground_station_flag[closest_groundstation["gid"]]==0:
                packet_sented=min(m_satellite_queue[satellite_id],ground_station_max_transmit_packets_per_time_step[closest_groundstation["gid"]])
                m_satellite_queue[satellite_id]-=packet_sented
                m_ground_station_queue[closest_groundstation["gid"]]+=packet_sented
                if(m_ground_station_queue[closest_groundstation["gid"]]>ground_station_max_cap):
                    # print("ground station "+str(closest_groundstation["gid"])+" overflow")
                    dis=m_ground_station_queue[closest_groundstation["gid"]]-ground_station_max_cap
                    m_ground_station_queue[closest_groundstation["gid"]]=ground_station_max_cap
                    packet_sented-=dis
                ground_station_flag[closest_groundstation["gid"]]=1
            else:
            ########################################
                max_dis=inf
                closest_groundstation=None
                for groundstation in ground_stations:
                    dis=dist_sat_gragh[satellite_id][satellite_choose[groundstation["gid"]]]
                    if dis<max_dis:
                        max_dis=dis
                        closest_groundstation=groundstation["gid"]
                if closest_groundstation!=None:
                    if satellite_choose[closest_groundstation]!=satellite_id:
                        dis=inf
                        next_hop_satellite=None
                        for neighbor in G.neighbors(satellite_id):
                            if(dist_sat_gragh[neighbor][satellite_choose[closest_groundstation]]<dis):
                                dis=dist_sat_gragh[neighbor][satellite_choose[closest_groundstation]]
                                next_hop_satellite=neighbor
                        if next_hop_satellite!=None:
                            packet_sented=min(m_satellite_queue[satellite_id],isl_max_cap)
                            m_satellite_queue[satellite_id]-=packet_sented
                            m_satellite_queue[next_hop_satellite]+=packet_sented
                        else:
                            print("error!")
                    else:
                        packet_sented=min(packet_sented,ground_station_max_transmit_packets_per_time_step[closest_groundstation])
                        m_satellite_queue[satellite_id]-=packet_sented
                        m_ground_station_queue[closest_groundstation]+=packet_sented
                        if(m_ground_station_queue[closest_groundstation]>ground_station_max_cap):
                        # print("ground station "+str(closest_groundstation["gid"])+" overflow")
                            dis=m_ground_station_queue[closest_groundstation]-ground_station_max_cap
                            m_ground_station_queue[closest_groundstation]=ground_station_max_cap
                            packet_sented-=dis
                        ground_station_flag[closest_groundstation]=1
        for groundstation in ground_stations:
            pre=m_ground_station_queue[groundstation["gid"]]
            m_ground_station_queue[groundstation["gid"]]-=ground_station_handle_packages_per_time_step[groundstation["gid"]]
            m_ground_station_queue[groundstation["gid"]]=max(0,m_ground_station_queue[groundstation["gid"]])
            total_throughput+=pre-m_ground_station_queue[groundstation["gid"]]
        throughput_table_with_isl.append(total_throughput)
    print("sim complete")
    return throughput_table_with_isl