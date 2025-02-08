// node on a 2d graph
export interface Node {
    x: number
    y: number
}

// rect node
export interface RectNode extends Node {
    width: number
    height: number
}

export function rectIntersect(rect1: RectNode, rect2: RectNode) {
    if (
        rect1.x + rect1.width < rect2.x ||
        rect2.x + rect2.width < rect1.x ||
        rect1.y + rect1.height < rect2.y ||
        rect2.y + rect2.height < rect1.y
    ) {
        return false;
    } else {
        return true;
    }
}

const graphicNode = (
    node: Node | RectNode,
    xScale: (x: number) => number = (x: number) => x,
    yScale: (y: number) => number = (y: number) => y,
) => {
    const { data, ...gNode } = node
    gNode.x = xScale(node.x)
    gNode.y = yScale(node.y)
    return gNode
}

export function GraphicNode() {
    let xScale = (x: number) => x
    let yScale = (y: number) => y

    this.xScale = (_) => {
        if (!_.length) return xScale
        xScale = _
        return this
    }
    this.yScale = (_) => {
        if (!_.length) return yScale
        yScale = _
        return this
    }
    this.node = (node: Node, rescale: boolean = true) => (
        rescale ? graphicNode(node, xScale, yScale)
            : graphicNode(node)
    )
    this.nodes = (...nodes: Node[]) => {
        return nodes.map(
            (node) => graphicNode(node, xScale, yScale)
        )
    }
}
