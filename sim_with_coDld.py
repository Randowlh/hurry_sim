import networkx as nx
import astropy.units as u
import distant_tools
import caculation_brand
from networkx.algorithms import bipartite
import numpy as np
from ortools.graph import pywrapgraph

def caculate_coDld(all_G,satellite_O):
    rout_dict=[]
    for i in range(len(satellite_O)):
        rout_dict.append({})
    loop_count=0
    while(True):
        # print("looped")
        loop_count+=1
        # print("looped")
        G = nx.Graph()
        U, V = set(), set()
        total_u=0
        total_v=0
        # Assign nodes to U or V based on the sign of elements in A
        for i, value in enumerate(satellite_O):
            if value > 0:
                U.add(i)
                total_u+=value
                # G.add_node(i, bipartite=0)
            elif value <= 0:
                V.add(i)
                total_v+=value
                # G.add_node(i, bipartite=1)
        # print("U: "+str(len(U))+" V: "+str(len(V)))
        # print("total_u: "+str(total_u)+" total_v: "+str(total_v))
        if(len(U)==0 or len(V)==0):
            break
      
        # print(len(U),len(V))
        # print(satellite_O)
        maxflow=pywrapgraph.SimpleMaxFlow()
        cnt=0
        for u in U:
            maxflow.AddArcWithCapacity(0,u+1,1)
        for v in V:
            maxflow.AddArcWithCapacity(v+1,len(satellite_O)+100,1)
        
        for edge in all_G.edges:
            if edge[0] in U and edge[1] in V:
                cnt+=1
                maxflow.AddArcWithCapacity(edge[0]+1,edge[1]+1,1)
                # G.add_edge(edge[0], edge[1])
                # print("added!")
                    # G.add_edge(v, u)
                    # print("added!")
        # print("cnt edge=",cnt)
        if cnt==0:
            break;
        if maxflow.Solve(0,len(satellite_O)+100) != maxflow.OPTIMAL:
            print("error")
            exit()
        for arc in range(maxflow.NumArcs()):
            if maxflow.Flow(arc) > 0 and maxflow.Head(arc) != len(satellite_O)+100 and maxflow.Tail(arc) != 0:
                sender = (maxflow.Tail(arc)-1) 
                receiver = (maxflow.Head(arc)-1) 
                if (sender!=receiver):
                    rout_dict[sender][receiver]=rout_dict[sender].get(receiver,0)+maxflow.Flow(arc)*1
                    satellite_O[sender]-=maxflow.Flow(arc)*1
                    satellite_O[receiver]+=maxflow.Flow(arc)*1

    print("looped "+str(loop_count)+" times")
        # max_matching = bipartite.maximum_matching(G)
        # pairs = [(u, v) for u, v in max_matching.items() if u in U]
        # for pair in pairs:
        #     rout_dict[pair[0]][pair[1]]=rout_dict[pair[0]].get(pair[1],0)+50
        #     satellite_O[pair[0]]-=50
        #     satellite_O[pair[1]]+=50
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
    for i in range(0, len(ground_stations)):
        ground_station_flag.append(0)
    # Create an empty graph

    G = nx.Graph()

    for i in range(len(satellites)):
        G.add_node(i)
    for edge in edges:
        G.add_edge(edge[0], edge[1])
        G.add_edge(edge[1], edge[0])
    # dist_matrix = nx.floyd_warshall_numpy(G)

    # print("safasdasfasfasf")
    routing_table=[]
    satellite_O=[]
    for i in range(len(satellites)):
        satellite_O.append(0)
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        # if time_since_epoch % (total_sim_time_ns // 100) == 0:
        for i in range(0, len(ground_stations)):
            ground_station_flag[i]=0
        print("coDld generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
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
        # print(satellite_O)
        rout_dict=caculate_coDld(G,satellite_O)
        
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