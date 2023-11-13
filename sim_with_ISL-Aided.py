import networkx as nx
import astropy.units as u
import distant_tools
import caculation_brand
from networkx.algorithms import bipartite

def create_graph(satellites, edges):
    G = nx.Graph()
    for i in range(len(satellites)):
        G.add_node(i)
    for edge in edges:
        G.add_edge(edge[0], edge[1])
    return G

def precompute_shortest_paths(G):
    # Compute and return the predecessor matrix
    pred, _ = nx.floyd_warshall_predecessor_and_distance(G)
    return pred

def reconstruct_path(pred, source, target):
    # Reconstruct the shortest path from the predecessor matrix
    try:
        path = [target]
        while path[-1] != source:
            path.append(pred[source][path[-1]])

        # Reverse the path to start from the source
        path.reverse()
        return path
    except KeyError:
        # KeyError means no path exists between source and target
        return []

def caculate_coDld(pred,satellite_O,rout_dict):
    while(True):
        G = nx.Graph()
        U, V = set(), set()
        # Assign nodes to U or V based on the sign of elements in A
        for i, value in enumerate(satellite_O):
            if value > 0:
                U.add(i)
                G.add_node(i, bipartite=0)
            elif value < 0:
                V.add(i)
                G.add_node(i, bipartite=1)
        if(len(U)==0 or len(V)==0):
            break
        for u in U:
            for v in V:
                G.add_edge(u, v)
        max_matching = bipartite.maximum_matching(G)
        pairs = [(u, v) for u, v in max_matching.items() if u in U]
        for pair in pairs:
            shortest_path=reconstruct_path(pred,pair[0],pair[1])
            for i in range(len(shortest_path)-1):
                rout_dict[shortest_path[i]][shortest_path[i+1]]=rout_dict[shortest_path[i]].get([shortest_path[i+1]],0)+1
            satellite_O[pair[0]]-=1
            satellite_O[pair[1]]+=1
    return rout_dict

def generate_with_coDld(satellites,
                 ground_stations,
                 edges,
                 total_sim_time_ns,
                 sim_time_step_ns,
                 epoch,
                 ground_station_max_transmit_packets_per_time_step,
                 max_gsl_length_m,
                 isl_max_cap,
                 satellite_generated_packages_per_time_step,
                 ):
    #init queue
    inf = 99999999999999
    ground_station_flag=[]
    throughput_table_with_isl=[]
    for i in range(0, len(ground_stations)):
        ground_station_flag.append(0)
    # Create an empty graph
    G = create_graph(satellites, edges)
    pred = precompute_shortest_paths(G)
    routing_table=[]
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        print("Simultion progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        routing_table_now=[now]
        satellite_O=[]

        for i in range(len(satellites)):
            routing_table_now.append([])
            satellite_O.append(satellite_generated_packages_per_time_step)
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
            satellite_O[closest_satellite]-=ground_station_max_transmit_packets_per_time_step[groundstation["gid"]]
        
        rout_dict=caculate_coDld(pred,satellite_O,routing_table_now)
        
        for i in range(len(satellites)):
            routing_table_now_satellite=[]
            for j in range(len(satellites)):
                if rout_dict[i].get(j,0)>0:
                    routing_table_now_satellite.append([j,rout_dict[i][j]])                
            routing_table_now.append(routing_table_now_satellite)
        routing_table.append(routing_table_now)

    print("sim complete")
    return routing_table