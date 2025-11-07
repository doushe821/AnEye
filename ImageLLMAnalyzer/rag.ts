import "dotenv/config"

import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory"
import { OpenAIEmbeddings }  from "@langchain/openai"

import * as z from "zod"
import { tool } from "@langchain/core/tools"
import { SystemMessage } from "@langchain/core/messages"
import { createAgent } from "langchain"

const embeddings = new OpenAIEmbeddings({
    model: "text-embedding-3-large"
});
const vectorStore = new MemoryVectorStore(embeddings);

const retrieveSchema = z.object({ query: z.string() });

const retrieve = tool(
    async ({ query }) => {
        const retrievedDocs = await vectorStore.similaritySearch(query, 2);
        const serialized = retrievedDocs.map(
            (doc) => "Source: ${doc.metadata.source}\nContent: ${doc.pageContent}"
        ).join("\n")
        return [serialized, retrievedDocs]
    },
    {
        name: "retrieve",
        description: "Retrieve info related to a query",
        schema: retrieveSchema,
        responseFormat: "content_and_artifact",
    }
);

const tools = [retrieve];
const sysPrompt = new SystemMessage(
    "You got the access to a tool that helps to retrieve context from a document." +
    "Use this tool to help answer user queries."
)

const agent = createAgent({model: "gpt-5", tools, sysPrompt})

// ------------------------------------------------------------

let input = "How to learn faster any language or skill faster ? ? ?"
let agentInput = {messages : [{role: "user", content: input}]};

const stream = await agent.stream(agentInput,  {
    streamMode : "values",
});

for await (const step of stream) {
    const lastMessage = step.messages[step.messages.length - 1];
    console.log('[$(lastMessage.role)]: $(lastMessage.content)');

}
