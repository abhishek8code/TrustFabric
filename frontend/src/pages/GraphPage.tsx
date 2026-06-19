import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { GraphViewer, GraphData } from "../components/GraphViewer";

export const GraphPage: React.FC = () => {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });

  useEffect(() => {
    api.get("/graph/neighbourhood/cust_001?depth=2").then((response) => setData(response.data));
  }, []);

  return <GraphViewer data={data} />;
};
