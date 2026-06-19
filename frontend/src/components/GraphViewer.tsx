import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export interface GraphNode {
  id: string;
  type: "customer" | "device" | "ip" | "beneficiary";
  risk: number;
  label: string;
}
export interface GraphLink {
  source: any;
  target: any;
  type: string;
}
export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export const GraphViewer: React.FC<{ data: GraphData }> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;

    const width = 700;
    const height = 480;
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current).attr("viewBox", `0 0 ${width} ${height}`);
    const riskColor = (r: number) => (r > 0.6 ? "#ef4444" : r > 0.3 ? "#f97316" : "#22c55e");

    const simulation = d3.forceSimulation(data.nodes as any)
      .force("link", d3.forceLink(data.links as any).id((d: any) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g").selectAll("line")
      .data(data.links).enter().append("line")
      .attr("stroke", "#334155").attr("stroke-width", 1.5);

    const node = svg.append("g").selectAll("circle")
      .data(data.nodes).enter().append("circle")
      .attr("r", (d: any) => (d.type === "customer" ? 12 : 8))
      .attr("fill", (d: any) => riskColor(d.risk))
      .attr("stroke", "#0f172a").attr("stroke-width", 2)
      .call(d3.drag<any, any>()
        .on("start", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    const label = svg.append("g").selectAll("text")
      .data(data.nodes).enter().append("text")
      .text((d: any) => d.label)
      .attr("fill", "#cbd5e1").attr("font-size", 10)
      .attr("dx", 14).attr("dy", 4);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    return () => {
      simulation.stop();
    };
  }, [data]);

  return (
    <div className="glass rounded-2xl p-4 shadow-glow">
      <h3 className="text-slate-300 font-semibold mb-3 text-sm uppercase tracking-wider">Identity Trust Graph — Fraud Ring View</h3>
      <svg ref={svgRef} className="w-full" style={{ height: 480 }} />
      <div className="flex gap-4 mt-3 text-xs text-slate-400">
        <span><span className="inline-block w-3 h-3 rounded-full bg-red-500 mr-1" />High Risk</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-orange-500 mr-1" />Medium</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1" />Clear</span>
      </div>
    </div>
  );
};
