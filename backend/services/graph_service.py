from __future__ import annotations

from collections import defaultdict

import networkx as nx


class GraphService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GraphService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.G = nx.Graph()
        self._confirmed_fraudsters: set[str] = set()
        self._initialized = True
        self._load_initial_graph()

    def _load_initial_graph(self):
        # Legitimate users
        self.add_login_event("cust_001", "dev_web_bob_demo", "192.168.1.15", "session_001")
        self.add_login_event("cust_002", "dev_phone_arjun", "192.168.1.16", "session_002")
        self.add_login_event("cust_003", "dev_phone_kavita", "192.168.1.17", "session_003")
        
        # Fraud ring sharing a device
        self.add_login_event("cust_fraud_001", "dev_mule_shared", "198.51.100.42", "session_f1")
        self.add_login_event("cust_mule_001", "dev_mule_shared", "198.51.100.43", "session_m1")
        self.add_login_event("cust_mule_002", "dev_mule_shared", "198.51.100.44", "session_m2")
        self.add_login_event("cust_mule_003", "dev_mule_shared", "198.51.100.45", "session_m3")

        # Mark confirmed fraud and run community detection
        self.mark_confirmed_fraud("cust_fraud_001")
        self.run_community_detection()

    def _risk_for(self, node: str) -> float:
        if self.G.has_node(node):
            return float(self.G.nodes[node].get("risk", 0.0))
        return 0.0

    def add_login_event(self, customer_id: str, device_fp: str, ip_address: str, session_id: str):
        cnode = f"customer:{customer_id}"
        dnode = f"device:{device_fp}"
        inode = f"ip:{ip_address}"
        self.G.add_node(cnode, type="customer", id=customer_id, risk=self._risk_for(cnode))
        self.G.add_node(dnode, type="device", id=device_fp, risk=self._risk_for(dnode))
        self.G.add_node(inode, type="ip", id=ip_address, risk=self._risk_for(inode))
        self.G.add_edge(cnode, dnode, type="USED_DEVICE", session=session_id)
        self.G.add_edge(cnode, inode, type="LOGGED_FROM", session=session_id)

    def add_transaction_event(self, customer_id: str, beneficiary_hash: str, amount: float, transaction_id: str):
        cnode = f"customer:{customer_id}"
        bnode = f"beneficiary:{beneficiary_hash}"
        self.G.add_node(cnode, type="customer", id=customer_id, risk=self._risk_for(cnode))
        self.G.add_node(bnode, type="beneficiary", id=beneficiary_hash, risk=self._risk_for(bnode))
        self.G.add_edge(cnode, bnode, type="TRANSFERRED_TO", tx_id=transaction_id, weight=min(1.0, amount / 100000.0))

    def mark_confirmed_fraud(self, customer_id: str):
        node = f"customer:{customer_id}"
        self._confirmed_fraudsters.add(node)
        self.G.add_node(node, type="customer", id=customer_id, risk=1.0)
        self.G.nodes[node]["risk"] = 1.0

    def run_community_detection(self):
        if self.G.number_of_nodes() < 3:
            return
        try:
            import community as community_louvain

            partition = community_louvain.best_partition(self.G)
            communities: dict[int, list[str]] = defaultdict(list)
            for node, comm_id in partition.items():
                communities[comm_id].append(node)
        except Exception:
            communities = {}
            for idx, community in enumerate(nx.algorithms.community.greedy_modularity_communities(self.G)):
                communities[idx] = list(community)

        for members in communities.values():
            fraudster_count = sum(1 for member in members if member in self._confirmed_fraudsters)
            community_risk = fraudster_count / max(1, len(members))
            for node in members:
                current_risk = self.G.nodes[node].get("risk", 0.0)
                self.G.nodes[node]["risk"] = max(current_risk, community_risk)

    def get_node_risk(self, customer_id: str) -> float:
        node = f"customer:{customer_id}"
        if not self.G.has_node(node):
            return 0.0
        return float(self.G.nodes[node].get("risk", 0.0))

    def get_neighbourhood_json(self, customer_id: str, depth: int = 2) -> dict:
        centre = f"customer:{customer_id}"
        if not self.G.has_node(centre):
            return {"nodes": [], "links": []}
        ego = nx.ego_graph(self.G, centre, radius=depth)
        nodes = []
        for n, data in ego.nodes(data=True):
            nodes.append({"id": n, "type": data.get("type", "unknown"), "risk": round(data.get("risk", 0.0), 3), "label": data.get("id", n)[:12]})
        links = [{"source": u, "target": v, "type": data.get("type", "")} for u, v, data in ego.edges(data=True)]
        return {"nodes": nodes, "links": links}
