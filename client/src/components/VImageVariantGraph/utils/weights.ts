const jsonCopy = (o: object) => {
    return o ? JSON.parse(JSON.stringify(o)) : o;
}

export const sortImagesByWeight = (images, edges, edgeGroups) => {
    const _images = calculateImageWeights(images, edges, edgeGroups);
    return _images.sort((a, b) => b.weight - a.weight).map((d) => d.index);
}

const calculateImageWeights = (images, edges, edgeGroups) => {
    const _images = jsonCopy(images);
    for (const img of _images) {
        img.weight = 0;
    }

    for (const group of edgeGroups) {
        group.edges.forEach((e) => {
            const edge = edges[e];
            _images[edge.src].weight += edge.weight;
            _images[edge.tgt].weight += edge.weight;
        });
    }

    return _images;
}
