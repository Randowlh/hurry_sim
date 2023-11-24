import networkx as nx
import astropy.units as u
import distant_tools
import caculation_brand
def generate_with_test(satellites,
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
    # dist_sat_gragh=nx.floyd_warshall_numpy(G)
    routing_table=[]
    
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        print("test generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        routing_table_now=[now]
        for satellite_id in range(0,len(satellites)):
            # print("satellite_id",satellite_id)
            routing_table_now_satellite=[]
            for neibor in G.neighbors(satellite_id):
                routing_table_now_satellite.append([neibor,isl_max_cap])
                break
            routing_table_now.append(routing_table_now_satellite)
        routing_table.append(routing_table_now)

    print("sim complete")
    # print("routing_table",routing_table)
    return routing_table