import type { RectNode } from './node'
import { rectIntersect } from './node'
import { BubbleSet, PointPath, ShapeSimplifier, BSplineShapeGenerator } from '../utils/bubblesets'

export const bubbleOutline = (
    rects: RectNode[],
    otherRects: RectNode[] = [],
    padding: number = 0
) => {
    const bubbles = new BubbleSet()
    const list = bubbles.createOutline(
        BubbleSet.addPadding(rects, padding),
        BubbleSet.addPadding(otherRects, padding),
        null
    )
    const outline = new PointPath(list).transform([
        new ShapeSimplifier(0.0),
        new BSplineShapeGenerator(),
        new ShapeSimplifier(0.0)
    ])
    return outline
}
