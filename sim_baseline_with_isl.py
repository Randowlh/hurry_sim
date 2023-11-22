import networkx as nx
import astropy.units as u
import distant_tools
import caculation_brand
def generate_with_isl(satellites,
                 ground_stations,
                 edges,
                 total_sim_time_ns,
                 sim_time_step_ns,
                 epoch,
                 ground_station_max_transmit_packets_per_time_step,
                 max_gsl_length_m,
                 isl_max_cap
                 ):
    #init queue
    inf = 99999999999999
    ground_station_flag=[]
    throughput_table_with_isl=[]
    for i in range(0, len(ground_stations)):
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
    print("isl G",len(G.nodes),len(G.edges))
    dist_sat_gragh=nx.floyd_warshall_numpy(G)
    routing_table=[]
    
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        print("baseline isl generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        routing_table_now=[now]
        satellite_choose=[] 
        for groundstation in ground_stations:
            #finding the closest satellite
            max_dis=inf
            closest_satellite=-1
            satellite_id=0
            for satellite in satellites:
                dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellites[satellite_id],str(epoch),str(now))
                if dis<max_dis:
                    max_dis=dis
                    closest_satellite=satellite_id
                satellite_id+=1
            satellite_choose.append(closest_satellite)
        for satellite_id in range(0,len(satellites)):
            # print("satellite_id",satellite_id)
            routing_table_now_satellite=[]
            ########################################
            max_dis=max_gsl_length_m
            closest_groundstation=None
            for groundstation in ground_stations:
                dis=distant_tools.distance_m_ground_station_to_satellite(groundstation,satellites[satellite_id],str(epoch),str(now))
                if dis<max_dis:
                    max_dis=dis
                    closest_groundstation=groundstation
            if closest_groundstation!=None and ground_station_flag[closest_groundstation["gid"]]==0:
                # print("here download",satellite_id,"to",closest_groundstation["gid"])
                packet_sented=caculation_brand.calculate_rate(ground_station_max_transmit_packets_per_time_step[closest_groundstation["gid"]],satellites[satellite_id],closest_groundstation,epoch,now) 
                routing_table_now_satellite.append([closest_groundstation["gid"]+len(satellites),packet_sented])
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
                            packet_sented=isl_max_cap
                            routing_table_now_satellite.append([int(next_hop_satellite),packet_sented])
                        else:
                            print("error!")
            routing_table_now.append(routing_table_now_satellite)
        routing_table.append(routing_table_now)

    print("sim complete")
    return routing_table