import { curveCatmullRom, line } from 'd3'

import type { Node, RectNode } from './node'

const curveGenerator = line()
    .curve(curveCatmullRom.alpha(0.5))
    .x((d: Node | RectNode) => d.x)
    .y((d: Node | RectNode) => d.y)

export const taperedEdge = (src: Node, tgt: Node, mid: Node) => {
    const path = curveGenerator([src, mid, tgt])

    // a trivial approximation of tangent direction at mid point
    const dx = tgt.x - src.x
    const dy = tgt.y - src.y
    const theta = Math.atan2(dy, dx)

    // direction perpendicular to the tangent
    const phi = theta + Math.PI / 2

    // generate two points on the perpendicular line
    const offsetMid = 2
    const offsetSrc = offsetMid * 2
    const pm1 = {
        x: mid.x + offsetMid * Math.cos(phi),
        y: mid.y + offsetMid * Math.sin(phi),
    }
    const pm2 = {
        x: mid.x - offsetMid * Math.cos(phi),
        y: mid.y - offsetMid * Math.sin(phi),
    }
    const ps1 = {
        x: src.x + offsetSrc * Math.cos(phi),
        y: src.y + offsetSrc * Math.sin(phi),
    }
    const ps2 = {
        x: src.x - offsetSrc * Math.cos(phi),
        y: src.y - offsetSrc * Math.sin(phi),
    }

    // generate a path with tapered end
    const path1 = curveGenerator([ps1, pm1, tgt])
    const path2 = curveGenerator([tgt, pm2, ps2])
    const path_ = `${path1} L ${path2.slice(1)} Z`

    return path_

    return path
}
