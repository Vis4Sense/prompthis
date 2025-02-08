export type Annotator = {
    documents: (docs: string[][]) => Annotator
    documentsToAnnotate: (docs: string[][]) => Annotator
    annotate: () => string[]
}

export const Annotator = (): Annotator => {
    const docs: string[][] = []
    const docsToAnnotate: string[][] = []
    const termIDFs: Record<string, number> = {}

    /** Utils */

    // calculate idf
    const calculateTermIDF = (term: string) => {
        const totalNum = docs.length
        const num = docs.filter((doc) => doc.includes(term)).length
        return Math.log(totalNum / (1 + num))
    }
    const calculateTermIDFs = () => {
        const terms = [...new Set(docs.flat())]
        terms.forEach((term) => {
            termIDFs[term] = calculateTermIDF(term)
        })
    }

    // calculate tf
    const calculateTermTF = (term: string, doc: string[]) => {
        const num = doc.filter((word) => word === term).length
        return num / doc.length
    }

    /** Methods */

    const initialize = () => {
        calculateTermIDFs()
    }

    const annotate = () => {
        const doc = docsToAnnotate.flat()
        const terms = [...new Set(doc)]
        const tfidfs: Record<string, number> = {}
        terms.forEach((term) => {
            tfidfs[term] = calculateTermTF(term, doc) * termIDFs[term]
        })

        const docScores = docsToAnnotate.map((doc) => {
            const score = doc.reduce((acc, term) => acc + tfidfs[term], 0)
            return { doc, score }
        })

        // doc with the highest score
        const selectedDoc = docScores.sort((a, b) => b.score - a.score)[0]

        // rank terms in selected doc by tfidf
        const termsInSelectedDoc = [...new Set(selectedDoc.doc)]
        const rankedTerms = termsInSelectedDoc.sort((a, b) => tfidfs[b] - tfidfs[a]).filter((term) => term !== ',')
        const selectedTerms = rankedTerms.slice(0, 8)

        return selectedDoc.doc.filter((term) => selectedTerms.includes(term))
    }

    /** Prototypes */

    const documents = (docs_: string[][]) => {
        docs.push(...docs_)
        initialize()
        return instance
    }

    const documentsToAnnotate = (docs_: string[][]) => {
        docsToAnnotate.length = 0
        docsToAnnotate.push(...docs_)
        return instance
    }

    /** Instance */
    const instance: Annotator = {
        documents,
        documentsToAnnotate,
        annotate
    }

    return instance
}
