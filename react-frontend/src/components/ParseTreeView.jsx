import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function ParseTreeView({ data }) {
  const containerRef = useRef();
  const svgRef = useRef();

  useEffect(() => {
    if (!data) return;

    const container = containerRef.current;
    const svgEl = d3.select(svgRef.current);
    svgEl.selectAll('*').remove();

    const W = container.clientWidth || 800;
    const H = container.clientHeight || 500;

    const root = d3.hierarchy(data);
    const nodeCount = root.descendants().length;
    const nodeWidth = Math.max(120, 1600 / nodeCount);
    const layout = d3.tree().nodeSize([nodeWidth, 80]);
    layout(root);

    // Center the tree
    const xs = root.descendants().map(d => d.x);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    
    svgEl.attr('width', W).attr('height', H);

    const zoom = d3.zoom().scaleExtent([0.1, 4]).on('zoom', e => {
      g.attr('transform', e.transform);
    });
    svgEl.call(zoom);

    const g = svgEl.append('g');
    const initTx = W / 2 - (minX + maxX) / 2;
    const initTy = 40;
    g.attr('transform', `translate(${initTx},${initTy})`);
    
    // Links
    g.selectAll('.link')
      .data(root.links())
      .join('path')
      .attr('class', 'link')
      .attr('d', d3.linkVertical().x(d => d.x).y(d => d.y));

    // Nodes
    const TERMINAL_TYPES = new Set([
      'Identifier','IntLiteral','FloatLiteral','CharLiteral','StringLiteral',
      'Type','Keyword','AssignOp','BinaryOp','UnaryOp'
    ]);

    const node = g.selectAll('.node')
      .data(root.descendants())
      .join('g')
      .attr('class', d => `node ${TERMINAL_TYPES.has(d.data.type) && !d.children ? 'terminal' : ''}`)
      .attr('transform', d => `translate(${d.x},${d.y})`);

    node.append('circle').attr('r', 18);

    const wrapLabel = (label, maxLen) => {
      if (label.length <= maxLen) return [label];
      const words = label.split(/\s+|(?<=[:=])/);
      const lines = [];
      let current = '';
      for (const w of words) {
        if ((current + w).length > maxLen) {
          if (current) lines.push(current.trim());
          current = w;
        } else {
          current += (current ? ' ' : '') + w;
        }
      }
      if (current) lines.push(current.trim());
      return lines.length ? lines : [label.slice(0, maxLen)];
    };

    // Label background
    node.each(function(d) {
      const label = d.data.name || d.data.type;
      const lines = wrapLabel(label, 14);
      const n = d3.select(this);

      const maxLen = Math.max(...lines.map(l => l.length));
      const bw = Math.max(40, maxLen * 6 + 8);
      const bh = lines.length * 13 + 4;

      n.append('rect')
        .attr('class', 'node-label-bg')
        .attr('x', -bw / 2)
        .attr('y', 22)
        .attr('width', bw)
        .attr('height', bh)
        .attr('rx', 3)
        .attr('fill', 'var(--surface)');

      lines.forEach((line, i) => {
        n.append('text')
          .attr('text-anchor', 'middle')
          .attr('x', 0)
          .attr('y', 32 + i * 13)
          .text(line);
      });
    });

    // Cleanup
    const handleZoomIn = () => svgEl.transition().call(zoom.scaleBy, 1.4);
    const handleZoomOut = () => svgEl.transition().call(zoom.scaleBy, 0.7);
    const handleReset = () => svgEl.transition().call(zoom.transform, d3.zoomIdentity.translate(initTx, initTy));

    const zoomInBtn = document.getElementById('tree-zoom-in');
    const zoomOutBtn = document.getElementById('tree-zoom-out');
    const resetBtn = document.getElementById('tree-reset');

    zoomInBtn?.addEventListener('click', handleZoomIn);
    zoomOutBtn?.addEventListener('click', handleZoomOut);
    resetBtn?.addEventListener('click', handleReset);

    return () => {
      zoomInBtn?.removeEventListener('click', handleZoomIn);
      zoomOutBtn?.removeEventListener('click', handleZoomOut);
      resetBtn?.removeEventListener('click', handleReset);
    };
  }, [data]);

  if (!data) return null;

  return (
    <div id="tree-container" ref={containerRef}>
      <svg id="tree-svg" ref={svgRef}></svg>
      <div className="tree-controls">
        <button className="tree-btn" id="tree-zoom-in" title="Zoom in">+</button>
        <button className="tree-btn" id="tree-zoom-out" title="Zoom out">−</button>
        <button className="tree-btn" id="tree-reset" title="Reset view">⌖</button>
      </div>
    </div>
  );
}
