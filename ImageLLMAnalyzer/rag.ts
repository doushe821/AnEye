// okay, i want to build an agent with rag
// even though, i don't know typescript hahah

// so, let's think more. what do i need?

// 1. i need a document (got it)
// 2. i need to extract text from it
// 3. then convert into embeddings

import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf.mjs";
import { RecursiveCharacterTextSplitter } from "la"

async function readPDF(filePath : string) {
    const loadingTask = pdfjsLib.getDocument(filePath);
    const pdf = await loadingTask.promise;
    let text = '';
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        content.items.forEach((item: any) => {
            text += item.str
        });
    }
    return text;
}

async function splitText(text, chunkSize, overlap) {

}

readPDF("./Documents/BEBRA.pdf")
