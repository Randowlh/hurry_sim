import networkx as nx
import astropy.units as u
import distant_tools
import caculation_brand
from networkx.algorithms import bipartite
import numpy as np

def find_shortest_path(G,dist_matrix, source, target):
    # 使用 floyd_warshall_numpy 来计算最短路径长度
    # 从距离矩阵中获取源点到目标点的距离
    dist = dist_matrix[source, target]
    # 如果距离为无穷大，说明没有路径
    if np.isinf(dist):
        return []

    # 重建最短路径
    path = [source]
    while path[-1] != target:
        current = path[-1]
        # 查找到达目标的下一个节点
        for neighbor in G.neighbors(current):
            if dist_matrix[neighbor, target] < dist:
                path.append(neighbor)
                dist = dist_matrix[neighbor, target]
                break
    return path

def caculate_coDld(all_G,dist_matrix,satellite_O):
    rout_dict=[]
    for i in range(len(satellite_O)):
        rout_dict.append({})
    while(True):
        # print("looped")
        G = nx.Graph()
        U, V = set(), set()
        # Assign nodes to U or V based on the sign of elements in A
        for i, value in enumerate(satellite_O):
            if value > 10000:
                U.add(i)
                G.add_node(i, bipartite=0)
            elif value < -10000:
                V.add(i)
                G.add_node(i, bipartite=1)
        if(len(U)==0 or len(V)==0):
            break
        # print(len(U),len(V))
        # print(satellite_O)
        for u in U:
            for v in V:
                G.add_edge(u, v)
        max_matching = bipartite.maximum_matching(G)
        pairs = [(u, v) for u, v in max_matching.items() if u in U]
        for pair in pairs:
            shortest_path=find_shortest_path(all_G,dist_matrix,pair[0],pair[1])
            for i in range(len(shortest_path)-1):
                rout_dict[shortest_path[i]][shortest_path[i+1]]=rout_dict[shortest_path[i]].get(shortest_path[i+1],0)+100
            satellite_O[pair[0]]-=5000
            satellite_O[pair[1]]+=5000
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
    print("here!!!!!!!!!!!!!")
    #init queue
    inf = 99999999999999
    ground_station_flag=[]
    for i in range(0, len(ground_stations)):
        ground_station_flag.append(0)
    # Create an empty graph

    G = nx.Graph()

    for i in range(len(satellites)):
        G.add_node(i)
    for edge in edges:
        G.add_edge(edge[0], edge[1],weight=1)
        G.add_edge(edge[1], edge[0],weight=1)
    dist_matrix = nx.floyd_warshall_numpy(G)

    print("safasdasfasfasf")
    routing_table=[]
    satellite_O=[]
    for i in range(len(satellites)):
        satellite_O.append(0)
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        print("coDit Simultion progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        total_throughput=0
        now=time_since_epoch*u.ns+epoch
        routing_table_now=[now]

        for i in range(len(satellites)):
            satellite_O[i]+=satellite_generated_packages_per_time_step
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
        rout_dict=caculate_coDld(G,dist_matrix,satellite_O)
        
        for i in range(len(satellites)):
            routing_table_now_satellite=[]
            for j in range(len(satellites)):
                if rout_dict[i].get(j,0)>0:
                    routing_table_now_satellite.append([j,rout_dict[i][j]])  
            for satellite_choose_id in range(len(satellite_choose)):
                if satellite_choose[satellite_choose_id]==i:
                    routing_table_now_satellite.append([len(satellites)+satellite_choose_id,ground_station_max_transmit_packets_per_time_step[ground_stations[satellite_choose_id]["gid"]]])              
                    # print("added!")
                    # print([len(satellites)+satellite_choose_id,ground_station_max_transmit_packets_per_time_step[ground_stations[satellite_choose_id]["gid"]]])
            routing_table_now.append(routing_table_now_satellite)
        routing_table.append(routing_table_now)
        
    # print(routing_table)
    print("sim complete")
    return routing_table