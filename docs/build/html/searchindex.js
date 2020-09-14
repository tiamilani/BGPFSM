Search.setIndex({docnames:["analysis","analyzer","bgp_sim","config","distribution","event","events","fsm","index","link","log","module","modules","node","node_BACKUP_25380","node_BACKUP_26214","node_BASE_25380","node_BASE_26214","node_LOCAL_25380","node_LOCAL_26214","node_REMOTE_25380","node_REMOTE_26214","packet","plotter","policies","rib","route","routingTable","singleton","transition"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["analysis.rst","analyzer.rst","bgp_sim.rst","config.rst","distribution.rst","event.rst","events.rst","fsm.rst","index.rst","link.rst","log.rst","module.rst","modules.rst","node.rst","node_BACKUP_25380.rst","node_BACKUP_26214.rst","node_BASE_25380.rst","node_BASE_26214.rst","node_LOCAL_25380.rst","node_LOCAL_26214.rst","node_REMOTE_25380.rst","node_REMOTE_26214.rst","packet.rst","plotter.rst","policies.rst","rib.rst","route.rst","routingTable.rst","singleton.rst","transition.rst"],objects:{"":{analysis:[0,0,0,"-"],analyzer:[1,0,0,"-"],bgp_sim:[2,0,0,"-"],config:[3,0,0,"-"],distribution:[4,0,0,"-"],event:[5,0,0,"-"],events:[6,0,0,"-"],fsm:[7,0,0,"-"],link:[9,0,0,"-"],log:[10,0,0,"-"],module:[11,0,0,"module-0"],node:[13,0,0,"-"],node_BACKUP_25380:[14,0,0,"-"],node_BACKUP_26214:[15,0,0,"-"],node_BASE_25380:[16,0,0,"-"],node_BASE_26214:[17,0,0,"-"],node_LOCAL_25380:[18,0,0,"-"],node_LOCAL_26214:[19,0,0,"-"],node_REMOTE_25380:[20,0,0,"-"],node_REMOTE_26214:[21,0,0,"-"],packet:[22,0,0,"-"],plotter:[23,0,0,"-"],policies:[24,0,0,"-"],rib:[25,0,0,"-"],route:[26,0,0,"-"],routingTable:[27,0,0,"-"],singleton:[28,0,0,"-"],transition:[29,0,0,"-"]},"analysis.SingleFileAnalysis":{NoneType:[0,1,1,""],ROUTE_COUNTER:[0,2,1,""],__init__:[0,3,1,""],col_types:[0,2,1,""],df:[0,3,1,""],dump_df:[0,3,1,""],dump_states:[0,3,1,""],dump_transitions:[0,3,1,""],evaluate_fsm:[0,3,1,""],evaluate_signaling:[0,3,1,""],get_out_signal:[0,3,1,""],get_route_df:[0,3,1,""],get_states_as_df:[0,3,1,""],get_states_route_df:[0,3,1,""],get_transitions_as_df:[0,3,1,""],keep_only_fsm_events:[0,3,1,""],selectNode:[0,3,1,""]},"config.Config":{OUTPUT:[3,2,1,""],__init__:[3,3,1,""],compute_output_file_name:[3,3,1,""],get_output_file:[3,3,1,""],get_param:[3,3,1,""],get_params:[3,3,1,""],get_runs_count:[3,3,1,""],map_parameters:[3,3,1,""],remove_comments:[3,3,1,""],set_run_number:[3,3,1,""]},"distribution.Const":{__init__:[4,3,1,""],get_value:[4,3,1,""]},"distribution.Distribution":{CONSTANT:[4,2,1,""],DISTRIBUTION:[4,2,1,""],EXPONENTIAL:[4,2,1,""],INT:[4,2,1,""],LAMBDA:[4,2,1,""],MAX:[4,2,1,""],MEAN:[4,2,1,""],MIN:[4,2,1,""],UNIFORM:[4,2,1,""],__init__:[4,3,1,""],get_value:[4,3,1,""]},"distribution.Exp":{__init__:[4,3,1,""],get_value:[4,3,1,""]},"distribution.Uniform":{__init__:[4,3,1,""],get_value:[4,3,1,""]},"event.Event":{__init__:[5,3,1,""],destination:[5,3,1,""],event_cause:[5,3,1,""],event_counter:[5,2,1,""],event_duration:[5,3,1,""],event_type:[5,3,1,""],id:[5,3,1,""],obj:[5,3,1,""],sent_time:[5,3,1,""],source:[5,3,1,""]},"events.Events":{DST_ADD:[6,2,1,""],NEW_DST:[6,2,1,""],NEW_PATH:[6,2,1,""],REANNOUNCE:[6,2,1,""],RIB_CHANGE:[6,2,1,""],RT_CHANGE:[6,2,1,""],RX:[6,2,1,""],STATE_CHANGE:[6,2,1,""],TX:[6,2,1,""],WITHDRAW:[6,2,1,""]},"link.Link":{DELAY:[9,2,1,""],POLICY_FUNCTION:[9,2,1,""],__init__:[9,3,1,""],delay:[9,3,1,""],id:[9,3,1,""],node:[9,3,1,""],test:[9,3,1,""],transmit:[9,3,1,""],tx:[9,3,1,""]},"log.Log":{__init__:[10,3,1,""],log_packet_rx:[10,3,1,""],log_packet_tx:[10,3,1,""],log_path:[10,3,1,""],log_rib_change:[10,3,1,""],log_rt_change:[10,3,1,""],log_state:[10,3,1,""]},"module.Module":{__init__:[11,3,1,""],get_id:[11,3,1,""],get_type:[11,3,1,""],handle_event:[11,3,1,""],initialize:[11,3,1,""]},"node.Node":{IDLE:[13,2,1,""],PAR_DATARATE:[13,2,1,""],PAR_DELAY:[13,2,1,""],PAR_IMPLICIT_WITHDRAW:[13,2,1,""],PAR_PROC_TIME:[13,2,1,""],PAR_REANNOUNCE:[13,2,1,""],PAR_REANNOUNCE_DIST:[13,2,1,""],PAR_SIGNALING:[13,2,1,""],PAR_SIGNALING_SEQUENCE:[13,2,1,""],PAR_WITHDRAW:[13,2,1,""],PAR_WITHDRAW_DIST:[13,2,1,""],STATE_CHANGING:[13,2,1,""],__init__:[13,3,1,""],add_destination:[13,3,1,""],add_neighbor:[13,3,1,""],change_state:[13,3,1,""],evaluate_signaling_event:[13,3,1,""],force_share_dst:[13,3,1,""],handle_event:[13,3,1,""],id:[13,3,1,""],neighbors:[13,3,1,""],new_network:[13,3,1,""],program_withdraw:[13,3,1,""],reannounce_handler:[13,3,1,""],rx_pkt:[13,3,1,""],send_msg_to_all:[13,3,1,""],share_dst:[13,3,1,""],state:[13,3,1,""],tx_pkt:[13,3,1,""]},"node_BACKUP_25380.Node":{IDLE:[14,2,1,""],PAR_DATARATE:[14,2,1,""],PAR_DELAY:[14,2,1,""],PAR_IMPLICIT_WITHDRAW:[14,2,1,""],PAR_PROC_TIME:[14,2,1,""],PAR_REANNOUNCE:[14,2,1,""],PAR_REANNOUNCE_DIST:[14,2,1,""],PAR_SIGNALING:[14,2,1,""],PAR_SIGNALING_SEQUENCE:[14,2,1,""],PAR_WITHDRAW:[14,2,1,""],PAR_WITHDRAW_DIST:[14,2,1,""],STATE_CHANGING:[14,2,1,""],__init__:[14,3,1,""],add_destination:[14,3,1,""],add_neighbor:[14,3,1,""],change_state:[14,3,1,""],evaluate_signaling_event:[14,3,1,""],force_share_dst:[14,3,1,""],handle_event:[14,3,1,""],id:[14,3,1,""],neighbors:[14,3,1,""],new_network:[14,3,1,""],program_withdraw:[14,3,1,""],reannounce_handler:[14,3,1,""],rx_pkt:[14,3,1,""],send_msg_to_all:[14,3,1,""],share_dst:[14,3,1,""],state:[14,3,1,""],tx_pkt:[14,3,1,""]},"node_BACKUP_26214.Node":{IDLE:[15,2,1,""],PAR_DATARATE:[15,2,1,""],PAR_DELAY:[15,2,1,""],PAR_IMPLICIT_WITHDRAW:[15,2,1,""],PAR_PROC_TIME:[15,2,1,""],PAR_REANNOUNCE:[15,2,1,""],PAR_REANNOUNCE_DIST:[15,2,1,""],PAR_SIGNALING:[15,2,1,""],PAR_SIGNALING_SEQUENCE:[15,2,1,""],PAR_WITHDRAW:[15,2,1,""],PAR_WITHDRAW_DIST:[15,2,1,""],STATE_CHANGING:[15,2,1,""],__init__:[15,3,1,""],add_destination:[15,3,1,""],add_neighbor:[15,3,1,""],change_state:[15,3,1,""],evaluate_signaling_event:[15,3,1,""],force_share_dst:[15,3,1,""],handle_event:[15,3,1,""],id:[15,3,1,""],neighbors:[15,3,1,""],new_network:[15,3,1,""],program_withdraw:[15,3,1,""],reannounce_handler:[15,3,1,""],rx_pkt:[15,3,1,""],send_msg_to_all:[15,3,1,""],share_dst:[15,3,1,""],state:[15,3,1,""],tx_pkt:[15,3,1,""]},"node_BASE_25380.Node":{IDLE:[16,2,1,""],PAR_DATARATE:[16,2,1,""],PAR_DELAY:[16,2,1,""],PAR_IMPLICIT_WITHDRAW:[16,2,1,""],PAR_PROC_TIME:[16,2,1,""],PAR_REANNOUNCE:[16,2,1,""],PAR_REANNOUNCE_DIST:[16,2,1,""],PAR_SIGNALING:[16,2,1,""],PAR_SIGNALING_SEQUENCE:[16,2,1,""],PAR_WITHDRAW:[16,2,1,""],PAR_WITHDRAW_DIST:[16,2,1,""],STATE_CHANGING:[16,2,1,""],__init__:[16,3,1,""],add_destination:[16,3,1,""],add_neighbor:[16,3,1,""],change_state:[16,3,1,""],evaluate_signaling_event:[16,3,1,""],force_share_dst:[16,3,1,""],handle_event:[16,3,1,""],id:[16,3,1,""],neighbors:[16,3,1,""],new_network:[16,3,1,""],program_withdraw:[16,3,1,""],reannounce_handler:[16,3,1,""],rx_pkt:[16,3,1,""],share_dst:[16,3,1,""],state:[16,3,1,""],tx_pkt:[16,3,1,""]},"node_BASE_26214.Node":{IDLE:[17,2,1,""],PAR_DATARATE:[17,2,1,""],PAR_DELAY:[17,2,1,""],PAR_IMPLICIT_WITHDRAW:[17,2,1,""],PAR_PROC_TIME:[17,2,1,""],PAR_REANNOUNCE:[17,2,1,""],PAR_REANNOUNCE_DIST:[17,2,1,""],PAR_SIGNALING:[17,2,1,""],PAR_SIGNALING_SEQUENCE:[17,2,1,""],PAR_WITHDRAW:[17,2,1,""],PAR_WITHDRAW_DIST:[17,2,1,""],STATE_CHANGING:[17,2,1,""],__init__:[17,3,1,""],add_destination:[17,3,1,""],add_neighbor:[17,3,1,""],change_state:[17,3,1,""],evaluate_signaling_event:[17,3,1,""],force_share_dst:[17,3,1,""],handle_event:[17,3,1,""],id:[17,3,1,""],neighbors:[17,3,1,""],new_network:[17,3,1,""],program_withdraw:[17,3,1,""],reannounce_handler:[17,3,1,""],rx_pkt:[17,3,1,""],share_dst:[17,3,1,""],state:[17,3,1,""],tx_pkt:[17,3,1,""]},"node_LOCAL_25380.Node":{IDLE:[18,2,1,""],PAR_DATARATE:[18,2,1,""],PAR_DELAY:[18,2,1,""],PAR_IMPLICIT_WITHDRAW:[18,2,1,""],PAR_PROC_TIME:[18,2,1,""],PAR_REANNOUNCE:[18,2,1,""],PAR_REANNOUNCE_DIST:[18,2,1,""],PAR_SIGNALING:[18,2,1,""],PAR_SIGNALING_SEQUENCE:[18,2,1,""],PAR_WITHDRAW:[18,2,1,""],PAR_WITHDRAW_DIST:[18,2,1,""],STATE_CHANGING:[18,2,1,""],__init__:[18,3,1,""],add_destination:[18,3,1,""],add_neighbor:[18,3,1,""],change_state:[18,3,1,""],evaluate_signaling_event:[18,3,1,""],force_share_dst:[18,3,1,""],handle_event:[18,3,1,""],id:[18,3,1,""],neighbors:[18,3,1,""],new_network:[18,3,1,""],program_withdraw:[18,3,1,""],reannounce_handler:[18,3,1,""],rx_pkt:[18,3,1,""],share_dst:[18,3,1,""],state:[18,3,1,""],tx_pkt:[18,3,1,""]},"node_LOCAL_26214.Node":{IDLE:[19,2,1,""],PAR_DATARATE:[19,2,1,""],PAR_DELAY:[19,2,1,""],PAR_IMPLICIT_WITHDRAW:[19,2,1,""],PAR_PROC_TIME:[19,2,1,""],PAR_REANNOUNCE:[19,2,1,""],PAR_REANNOUNCE_DIST:[19,2,1,""],PAR_SIGNALING:[19,2,1,""],PAR_SIGNALING_SEQUENCE:[19,2,1,""],PAR_WITHDRAW:[19,2,1,""],PAR_WITHDRAW_DIST:[19,2,1,""],STATE_CHANGING:[19,2,1,""],__init__:[19,3,1,""],add_destination:[19,3,1,""],add_neighbor:[19,3,1,""],change_state:[19,3,1,""],evaluate_signaling_event:[19,3,1,""],force_share_dst:[19,3,1,""],handle_event:[19,3,1,""],id:[19,3,1,""],neighbors:[19,3,1,""],new_network:[19,3,1,""],program_withdraw:[19,3,1,""],reannounce_handler:[19,3,1,""],rx_pkt:[19,3,1,""],share_dst:[19,3,1,""],state:[19,3,1,""],tx_pkt:[19,3,1,""]},"node_REMOTE_25380.Node":{IDLE:[20,2,1,""],PAR_DATARATE:[20,2,1,""],PAR_DELAY:[20,2,1,""],PAR_IMPLICIT_WITHDRAW:[20,2,1,""],PAR_PROC_TIME:[20,2,1,""],PAR_REANNOUNCE:[20,2,1,""],PAR_REANNOUNCE_DIST:[20,2,1,""],PAR_SIGNALING:[20,2,1,""],PAR_SIGNALING_SEQUENCE:[20,2,1,""],PAR_WITHDRAW:[20,2,1,""],PAR_WITHDRAW_DIST:[20,2,1,""],STATE_CHANGING:[20,2,1,""],__init__:[20,3,1,""],add_destination:[20,3,1,""],add_neighbor:[20,3,1,""],change_state:[20,3,1,""],evaluate_signaling_event:[20,3,1,""],force_share_dst:[20,3,1,""],handle_event:[20,3,1,""],id:[20,3,1,""],neighbors:[20,3,1,""],new_network:[20,3,1,""],program_withdraw:[20,3,1,""],reannounce_handler:[20,3,1,""],rx_pkt:[20,3,1,""],send_msg_to_all:[20,3,1,""],share_dst:[20,3,1,""],state:[20,3,1,""],tx_pkt:[20,3,1,""]},"node_REMOTE_26214.Node":{IDLE:[21,2,1,""],PAR_DATARATE:[21,2,1,""],PAR_DELAY:[21,2,1,""],PAR_IMPLICIT_WITHDRAW:[21,2,1,""],PAR_PROC_TIME:[21,2,1,""],PAR_REANNOUNCE:[21,2,1,""],PAR_REANNOUNCE_DIST:[21,2,1,""],PAR_SIGNALING:[21,2,1,""],PAR_SIGNALING_SEQUENCE:[21,2,1,""],PAR_WITHDRAW:[21,2,1,""],PAR_WITHDRAW_DIST:[21,2,1,""],STATE_CHANGING:[21,2,1,""],__init__:[21,3,1,""],add_destination:[21,3,1,""],add_neighbor:[21,3,1,""],change_state:[21,3,1,""],evaluate_signaling_event:[21,3,1,""],force_share_dst:[21,3,1,""],handle_event:[21,3,1,""],id:[21,3,1,""],neighbors:[21,3,1,""],new_network:[21,3,1,""],program_withdraw:[21,3,1,""],reannounce_handler:[21,3,1,""],rx_pkt:[21,3,1,""],send_msg_to_all:[21,3,1,""],share_dst:[21,3,1,""],state:[21,3,1,""],tx_pkt:[21,3,1,""]},"packet.Packet":{UPDATE:[22,2,1,""],WITHDRAW:[22,2,1,""],__init__:[22,3,1,""],content:[22,3,1,""],fromString:[22,3,1,""],id:[22,3,1,""],packet_type:[22,3,1,""]},"plotter.Plotter":{__init__:[23,3,1,""],get_detailed_fsm_graphviz:[23,3,1,""],get_fsm_graphviz:[23,3,1,""],signaling_nmessage_probability:[23,3,1,""],states_stage_boxplot:[23,3,1,""]},"policies.PolicyFunction":{PASS_EVERYTHING:[24,2,1,""],__init__:[24,3,1,""],insert:[24,3,1,""],values:[24,3,1,""]},"policies.PolicyValue":{__init__:[24,3,1,""],fromString:[24,3,1,""],value:[24,3,1,""]},"rib.Rib":{__init__:[25,3,1,""],check:[25,3,1,""],contains:[25,3,1,""],filter:[25,3,1,""],get_key:[25,3,1,""],insert:[25,3,1,""],remove:[25,3,1,""],update_rib_state:[25,3,1,""]},"rib.RibIterator":{__init__:[25,3,1,""]},"route.Route":{__init__:[26,3,1,""],add_to_path:[26,3,1,""],addr:[26,3,1,""],fromString:[26,3,1,""],mine:[26,3,1,""],nh:[26,3,1,""],path:[26,3,1,""],policy_value:[26,3,1,""],remove_from_path:[26,3,1,""]},"routingTable.RoutingTable":{__init__:[27,3,1,""],check:[27,3,1,""],getKey:[27,3,1,""],insert:[27,3,1,""]},"routingTable.RoutingTableIterator":{__init__:[27,3,1,""]},"singleton.Singleton":{Instance:[28,3,1,""],__init__:[28,3,1,""]},"transition.Transition":{__init__:[29,3,1,""]},analysis:{SingleFileAnalysis:[0,1,1,""]},config:{Config:[3,1,1,""]},distribution:{Const:[4,1,1,""],Distribution:[4,1,1,""],Exp:[4,1,1,""],Uniform:[4,1,1,""]},event:{Event:[5,1,1,""]},events:{Events:[6,1,1,""]},link:{Link:[9,1,1,""]},log:{Log:[10,1,1,""]},module:{Module:[11,1,1,""]},node:{Node:[13,1,1,""]},node_BACKUP_25380:{Node:[14,1,1,""]},node_BACKUP_26214:{Node:[15,1,1,""]},node_BASE_25380:{Node:[16,1,1,""]},node_BASE_26214:{Node:[17,1,1,""]},node_LOCAL_25380:{Node:[18,1,1,""]},node_LOCAL_26214:{Node:[19,1,1,""]},node_REMOTE_25380:{Node:[20,1,1,""]},node_REMOTE_26214:{Node:[21,1,1,""]},packet:{Packet:[22,1,1,""]},plotter:{Plotter:[23,1,1,""]},policies:{PolicyFunction:[24,1,1,""],PolicyValue:[24,1,1,""]},rib:{Rib:[25,1,1,""],RibIterator:[25,1,1,""]},route:{Route:[26,1,1,""]},routingTable:{RoutingTable:[27,1,1,""],RoutingTableIterator:[27,1,1,""]},singleton:{Singleton:[28,1,1,""]},transition:{Transition:[29,1,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","attribute","Python attribute"],"3":["py","method","Python method"]},objtypes:{"0":"py:module","1":"py:class","2":"py:attribute","3":"py:method"},terms:{"case":3,"class":[0,3,4,5,6,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],"const":4,"default":[7,8,13,14,15,20,21,25],"final":29,"float":[0,4,9],"function":[0,3,9,11,13,14,15,16,17,18,19,20,21,22,23,24,25,28],"int":[0,4],"new":[10,13,14,15,20,21,25,28],"return":[0,3,4,5,9,11,13,14,15,20,21,22,23,24,25,26,28],"throw":[11,13,14,15,16,17,18,19,20,21],"true":[4,10,13,14,15,16,17,18,19,20,21,25],"try":28,For:[3,22,24],The:[3,9,10,13,14,15,20,21,24,26,28],Use:[2,7,8],Used:[10,25,29],__call__:28,__init__:[0,3,4,5,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],abc:[24,25,27],abl:9,about:[3,23],accept:[4,24],accur:28,activ:[13,14,15,20,21],actual:[9,24,25],add:[13,14,15,16,17,18,19,20,21,26],add_destin:[13,14,15,16,17,18,19,20,21],add_msg_before_exec:[],add_neighbor:[13,14,15,16,17,18,19,20,21],add_to_path:26,add_transmiss:[],added:[13,14,15,16,17,18,19,20,21],addit:3,addr:[25,26],address:[26,27],aforement:3,after:25,all:[0,6,11,13,14,15,16,17,18,19,20,21,28],alreadi:[10,13,14,15,16,17,18,19,20,21,28],also:[4,9,13,14,15,20,21,23],alwai:25,analysi:12,analyz:[0,23],ani:[9,27],append:25,appli:28,applic:9,argument:28,arrai:3,arriv:9,assign:[9,11,22],associ:[13,14,15,20,21,22,24,26],attach:5,attravers:[13,14,15,20,21],automat:[3,9,11,22],avail:[7,8],base:[0,3,4,5,6,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,26,27,28,29],basic:[5,11],befor:[3,9,13,14,15,16,17,18,19,20,21,25],begin:26,being:[4,28],best:[13,14,15,20,21],between:[4,9,24],bgp:2,bgp_sim:[],call:[11,28],can:[3,4,9,26,27,28],cannot:28,caracter:29,caus:[5,13,14,15,20,21,25,29],ceil:4,chang:[10,13,14,15,16,17,18,19,20,21],change_st:[13,14,15,16,17,18,19,20,21],channel:9,check:[25,27],classmethod:[0,3,22,24,26],client:24,col_typ:0,collect:[24,25,27],comment:3,compleat:[7,8],compos:24,comput:3,compute_output_file_nam:3,condifur:12,config:[4,7,8,12,13,14,15,16,17,18,19,20,21],config_fil:3,configur:[3,4,7,8,13,14,15,16,17,18,19,20,21],constant:4,constructor:[3,4,10,11],contain:[3,9,25,26,27],content:[3,22],control:12,convert:24,core:0,correctli:9,correspond:23,could:[22,25,26],count:3,counter:29,creat:[3,5,9,22,23,25,27,28,29],csv:[0,3,10],current:0,data:[10,16,17,18,19,23],datafram:[0,23],datar:[13,14,15,16,17,18,19,20,21],decor:28,defin:[3,5,6,7,8,9,10,11,22,28],defualt:[13,14,15,20,21],delai:[9,13,14,15,16,17,18,19,20,21],depend:4,descret:[7,8],destiant:[13,14,15,16,17,18,19,20,21],destin:[5,9,13,14,15,16,17,18,19,20,21,26],detail:23,detemin:24,determin:25,differ:[4,5,12,22,26],digraph:23,disabl:10,discret:[0,4],distribut:[3,9,12],dot:23,dst:10,dst_add:6,dump_df:0,dump_stat:0,dump_transit:0,dure:[22,29],each:[3,11,23],eas:28,easier:24,edg:[23,29],effect:[24,27],elem:[13,14,15,16,17,18,19,20,21],element:[5,13,14,15,20,21],emul:9,enabl:10,env:9,environ:[3,9],error:[11,13,14,15,16,17,18,19,20,21],evalu:[0,9,13,14,15,20,21,25],evaluate_fsm:0,evaluate_sign:0,evaluate_signaling_ev:[13,14,15,16,17,18,19,20,21],event:[0,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,25],event_caus:[0,5],event_count:5,event_dur:5,event_id:0,event_typ:5,everi:[9,26],everyth:24,exampl:[3,7,8,24],execut:[7,8],exist:10,exp:[3,4],experi:3,explan:[7,8],exponenti:4,fals:[0,4,10,13,14,15,16,17,18,19,20,21,25,26],far:4,file:[0,3,7,8,10,13,14,15,16,17,18,19,20,21,23],file_0:3,file_1:3,file_:3,filter:[12,25],first:28,flag:[13,14,15,20,21],follow:3,force_share_dst:[13,14,15,16,17,18,19,20,21],format:[0,3,4,10,13,14,15,20,21],fot:9,found:3,frame:0,from:[3,11,13,14,15,16,17,18,19,20,21,22,24,25,26,28],fromstr:[22,24,26],fsm:[0,29],gener:[4,5,11,13,14,15,16,17,18,19,20,21,22],get:[7,8,11,13,14,15,16,17,18,19,20,21,22,24,26,28],get_detailed_fsm_graphviz:23,get_fsm_graphviz:23,get_id:11,get_kei:25,get_out_sign:0,get_output_fil:3,get_param:3,get_route_df:0,get_runs_count:3,get_states_as_df:0,get_states_route_df:0,get_transitions_as_df:0,get_typ:11,get_valu:4,getkei:27,given:[3,24],goal:[9,24],goe:3,graph:[23,29],graphml:9,graphviz:23,handl:[11,12,13,14,15,16,17,18,19,20,21,25,27,29],handle_ev:[11,13,14,15,16,17,18,19,20,21],happen:29,has:[6,13,14,15,16,17,18,19,20,21,24,27],have:[3,7,8,9,13,14,15,20,21],head:[14,15],help:[7,8,28],helper:28,here:3,hop:[13,14,15,20,21],id_nod:[13,14,15,20,21],id_packet:22,identifi:[13,14,15,16,17,18,19,20,21,23],idl:[13,14,15,16,17,18,19,20,21],implement:[4,11,28],implicit_withdraw:[13,14,15,16,17,18,19,20,21,25],index:[3,8,25,27],indic:23,inf:24,inform:[0,3,10,12,23,26],inherit:[11,28],init_st:29,initi:[11,22,23,28,29],input:[24,29],inputfil:0,insert:[13,14,15,20,21,24,25,27],insid:[3,6,8,13,14,15,16,17,18,19,20,21,24],instanc:[11,27,28],instanti:[4,11],integ:4,introduc:23,introduct:25,isol:0,iter:[25,27],ith:25,its:[3,28],itself:24,json:[3,7,8],json_fil:3,keep_only_fsm_ev:0,kei:25,kick:[13,14,15,20,21],know:23,knowledg:[10,23],lambda:[3,4],like:[2,9],limit:28,link:[12,13,14,15,16,17,18,19,20,21],list:[7,8,13,14,15,20,21,24,26],load:3,lock:9,log:12,log_packet:10,log_packet_rx:10,log_packet_tx:10,log_path:10,log_rib_chang:10,log_routing_chang:10,log_rt_chang:10,log_stat:10,logger:25,logic:[13,14,15,20,21],lot:23,main:23,make:24,manag:[0,8,12,13,14,15,16,17,18,19,20,21,26],mandatori:[7,8],map:3,map_paramet:3,master:[14,15],math:24,max:4,maximum:4,mean:[4,10],meaning:0,messag:[9,23,24],message_identifi:[],metaclass:28,method:[11,26,27,28],min:4,mine:26,minimum:4,modifi:[5,23],modul:12,more:23,mroe:[7,8],msg:9,multipl:6,must:[5,24],mutablesequ:[24,25,27],name:[3,4,10],need:[0,3,9,13,14,15,16,17,18,19,20,21,25],neigh:[],neighbor:[8,13,14,15,16,17,18,19,20,21],neighbour:[13,14,15,20,21,25],network:[13,14,15,20,21],new_dst:6,new_network:[13,14,15,16,17,18,19,20,21],new_path:6,newli:11,next:[13,14,15,20,21],next_hop:[13,14,15,20,21],node:[0,9,10,16,17,18,19,25,27,29],node_backup_25380:[],node_backup_26214:[],node_base_25380:[],node_base_26214:[],node_id:[0,10,25],node_local_25380:[],node_local_26214:[],node_remote_25380:[],node_remote_26214:[],non:[3,28],none:[0,3,5,9,13,14,15,16,17,18,19,20,21,22,23,25],nonetyp:0,notifi:5,now:[22,25],number:[3,4,24,29],obatin:0,obj:5,object:[0,3,4,5,6,9,10,11,22,23,24,25,26,27,28,29],old:25,one:[3,27,28],onli:[0,13,14,15,20,21,24,25,27,28],oper:9,option:[0,5],ora:22,order_by_tim:0,origin:[13,14,15,16,17,18,19,20,21],other:[24,28],output:[0,3,10,24,29],output_fil:[0,10,23],output_st:29,overrid:25,overridden:11,overwritten:10,packet:[10,12,13,14,15,16,17,18,19,20,21],packet_typ:22,page:8,panda:0,par1:4,par2:4,par_datar:[13,14,15,16,17,18,19,20,21],par_delai:[13,14,15,16,17,18,19,20,21],par_implicit_withdraw:[13,14,15,16,17,18,19,20,21],par_proc_tim:[13,14,15,16,17,18,19,20,21],par_reannounc:[13,14,15,16,17,18,19,20,21],par_reannounce_dist:[13,14,15,16,17,18,19,20,21],par_sign:[13,14,15,16,17,18,19,20,21],par_signaling_sequ:[13,14,15,16,17,18,19,20,21],par_withdraw:[13,14,15,16,17,18,19,20,21],par_withdraw_dist:[13,14,15,16,17,18,19,20,21],param:[0,3,4,5,9,10,13,14,15,16,17,18,19,20,21,22,24],paramet:[0,3,4,7,8,9,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,29],particular:[3,10],pass:[13,14,15,20,21,24],pass_everyth:24,path:[10,13,14,15,16,17,18,19,20,21,26],per:[3,27],pleas:[7,8],plot:23,plotter:12,plu:29,point:[3,4],polici:[9,12,13,14,15,20,21,26],policy_funct:9,policy_valu:[9,13,14,15,16,17,18,19,20,21,26],policyfunct:24,policyvalu:[9,24,26],posit:24,possibl:[0,5,6,22,24,25,27],povid:25,prefer:9,present:[5,25],previusli:[13,14,15,16,17,18,19,20,21],process:[3,9,13,14,15,16,17,18,19,20,21],program:[13,14,15,16,17,18,19,20,21],program_withdraw:[13,14,15,16,17,18,19,20,21],properti:[0,5,9,13,14,15,16,17,18,19,20,21,22,24,26],protocol:[7,8],provid:24,python3:[7,8],queue:[16,17,18,19],raggrup:6,rais:[13,14,15,20,21,28],random:[3,4],rate:[],reach:[13,14,15,20,21,26],read:3,readm:[7,8],realli:23,reannounc:[6,13,14,15,16,17,18,19,20,21],reannounce_handl:[13,14,15,16,17,18,19,20,21],reannouncement_dist:[13,14,15,16,17,18,19,20,21],receiv:[13,14,15,16,17,18,19,20,21],recept:[13,14,15,16,17,18,19,20,21],redistribut:[13,14,15,16,17,18,19,20,21],refer:[7,8,9],referenc:9,regist:25,remov:[3,25,26],remove_com:3,remove_from_path:26,repres:[13,14,15,20,21,29],represent:[3,22,26],requir:[9,24],reserv:9,resourc:9,respect:[13,14,15,20,21],restrict:28,result:[3,10,23,24,28],retriv:23,rib:[10,12,13,14,15,20,21],rib_chang:[0,6],ribiter:25,rout:[10,12,13,14,15,16,17,18,19,20,21,23],route_count:0,route_df:0,route_id:23,routingt:12,routingtableiter:27,rt_chang:6,run:[2,3,7,8],run_numb:3,rx_pkt:[13,14,15,16,17,18,19,20,21],safe:28,schedul:[5,11],search:8,section:[3,7,8],see:28,seed:3,selectnod:0,self:28,send:[13,14,15,20,21],send_msg_to_al:[13,14,15,20,21],sent:[5,13,14,15,20,21],sent_tim:5,separ:24,set:[3,4,13,14,15,16,17,18,19,20,21],set_run_numb:3,share:[13,14,15,16,17,18,19,20,21,29],share_dst:[13,14,15,16,17,18,19,20,21],should:[5,11,13,14,15,20,21,28],sigal:[13,14,15,20,21],signal:[13,14,15,16,17,18,19,20,21,23],signaling_nmessage_prob:23,signaling_sequ:[13,14,15,16,17,18,19,20,21],signatur:28,simpi:9,simul:[0,2,3,6,7,8,11,13,14,15,16,17,18,19,20,21,22],singl:[0,9],singlefileanalysi:0,singleton:12,size:3,some:[10,11],sourc:[0,3,4,5,6,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],specif:[3,9],specifi:[3,4],standard:3,start:[13,14,15,20,21,29],starter:[13,14,15,20,21],state:[0,8,10,13,14,15,16,17,18,19,20,21,23,25,29],state_chang:[6,13,14,15,16,17,18,19,20,21],states_rout:0,states_stage_boxplot:23,stop:11,store:[13,14,15,16,17,18,19,20,21,26],str:[0,13,14,15,20,21,22,24,26],string:[22,24,26],structur:[5,16,17,18,19],studi:0,subsequ:28,substitut:24,system:[12,23],tabl:[10,12,13,14,15,20,21,23,25],take:28,termin:[13,14,15,16,17,18,19,20,21],test:[9,13,14,15,16,17,18,19,20,21],text:3,textual:3,than:[24,28],thi:[3,5,6,9,11,13,14,15,20,21,22,23,24,25,26,27,28],those:0,thread:28,time:[0,5,9,13,14,15,16,17,18,19,20,21,29],transfer:[9,24],transform:[22,24],transit:[0,12,23],transmiss:[9,13,14,15,16,17,18,19,20,21,22],transmit:[9,13,14,15,16,17,18,19,20,21],trasfer:9,trigger:[9,10,13,14,15,16,17,18,19,20,21],trigger_input:29,tupl:3,two:3,tx_pkt:[13,14,15,16,17,18,19,20,21],type:[0,5,6,9,11,13,14,15,20,21,22,24,25,28],typeerror:28,unif:4,uniform:4,uniqu:[9,22],uniqueid:9,unitari:9,updat:[22,25],update_rib_st:25,upon:28,use:[3,4,5,7,8,9,24,28],used:[3,4,5,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23,25,27,28,29],user:3,using:[3,25],util:10,valid:[13,14,15,20,21,24],valu:[0,3,4,9,13,14,15,20,21,24,25,26,27],valueerror:[13,14,15,20,21],variabl:[3,4,23],vector:25,voic:26,wai:10,wait:9,waiting_tim:[13,14,15,16,17,18,19,20,21],want:3,what:3,whcich:23,when:[13,14,15,20,21,24],where:[9,29],whether:4,which:[5,7,8,9,23,24],withdraw:[6,13,14,15,16,17,18,19,20,21,22],withdraw_dist:[13,14,15,16,17,18,19,20,21],without:3,write:0},titles:["analysis module","analyzer module","bgp_sim module","config module","distribution module","event module","events module","fsm module","Welcome to BGPFSM\u2019s documentation!","link module","log module","module module","util","node module","node_BACKUP_25380 module","node_BACKUP_26214 module","node_BASE_25380 module","node_BASE_26214 module","node_LOCAL_25380 module","node_LOCAL_26214 module","node_REMOTE_25380 module","node_REMOTE_26214 module","packet module","plotter module","policies module","rib module","route module","routingTable module","singleton module","transition module"],titleterms:{analysi:0,analyz:[1,8],argument:[7,8],base:25,bgp_sim:2,bgpfsm:8,condifur:3,config:3,control:[8,22,25],differ:3,distribut:4,document:8,event:[5,6],filter:24,fsm:[7,8],handl:[5,9,24,26],indic:8,inform:25,link:9,log:10,manag:[3,27],model:8,modul:[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],node:[8,13,14,15,20,21],node_backup_25380:14,node_backup_26214:15,node_base_25380:16,node_base_26214:17,node_local_25380:18,node_local_26214:19,node_remote_25380:20,node_remote_26214:21,packet:22,plotter:23,polici:24,rib:25,rout:[25,26,27],routingt:27,singleton:28,src:[],system:22,tabl:[8,27],test:[],transit:29,used:[24,26],util:12,welcom:8}})