from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4

class LinkFailureController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LinkFailureController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.primary_path_active = True

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.datapaths[datapath.id] = datapath
        self.install_primary_flows(datapath)
        self.install_arp_flows(datapath)

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                idle_timeout=idle_timeout,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    def delete_all_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        mod = parser.OFPFlowMod(datapath=datapath,
                                command=ofproto.OFPFC_DELETE,
                                out_port=ofproto.OFPP_ANY,
                                out_group=ofproto.OFPG_ANY,
                                match=match)
        datapath.send_msg(mod)

    def install_arp_flows(self, datapath):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        match = parser.OFPMatch(eth_type=0x0806)
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 5, match, actions)

    def install_primary_flows(self, datapath):
        parser = datapath.ofproto_parser
        dpid = datapath.id

        if dpid == 1:
            self.logger.info("=" * 50)
            self.logger.info("ACTIVE PATH: h1 -> s1 -> s2 -> h2 (Primary)")
            self.logger.info("=" * 50)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 10, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 10, match, actions)

        elif dpid == 2:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 10, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 10, match, actions)

        elif dpid == 3:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 10, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 10, match, actions)

    def install_backup_flows(self, datapath):
        parser = datapath.ofproto_parser
        dpid = datapath.id

        if dpid == 1:
            self.logger.info("=" * 50)
            self.logger.info("ACTIVE PATH: h1 -> s1 -> s3 -> s2 -> h2 (Backup)")
            self.logger.info("=" * 50)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 20, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 20, match, actions)

        elif dpid == 2:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 20, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 20, match, actions)

        elif dpid == 3:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.2')
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 20, match, actions)
            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst='10.0.0.1')
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 20, match, actions)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        ofproto = msg.datapath.ofproto
        port_no = msg.desc.port_no
        dpid = msg.datapath.id

        if reason == ofproto.OFPPR_MODIFY:
            if msg.desc.state & ofproto.OFPPS_LINK_DOWN:
                if dpid == 1 and port_no == 2:
                    self.logger.info("=" * 50)
                    self.logger.info("LINK FAILURE DETECTED on s1-s2! Switching to backup path.")
                    self.logger.info("=" * 50)
                    self.primary_path_active = False
                    for dp in self.datapaths.values():
                        self.delete_all_flows(dp)
                        self.install_backup_flows(dp)
                        self.install_arp_flows(dp)
            else:
                if dpid == 1 and port_no == 2:
                    self.logger.info("=" * 50)
                    self.logger.info("LINK RESTORED on s1-s2! Switching back to primary path.")
                    self.logger.info("=" * 50)
                    self.primary_path_active = True
                    for dp in self.datapaths.values():
                        self.delete_all_flows(dp)
                        self.install_primary_flows(dp)
                        self.install_arp_flows(dp)