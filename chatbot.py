import torch
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser



#================================================================================
# LINK EXTARCTION,  FETCH TRANSCRPT, FORMAT DOCUMNET FUNCTION
def extract_id(url):
    # If URL contains short format youtu.be/VIDEOID
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    # If URL contains watch?v=VIDEOID
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]

    # If URL contains /embed/VIDEOID
    if "/embed/" in url:
        return url.split("/embed/")[1].split("?")[0]

    # If URL contains /shorts/VIDEOID
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]

    return None


def fetch_transcrpit(url):
    video_id=extract_id(url)
    data=""
    try:
        api=YouTubeTranscriptApi()
        transcript = api.fetch("j5168Ug7DvA", languages=["en"])
        for item in transcript:
            data+=item.text
        return data
    except Exception as e:
        print(e)
        return None

def format_doc(context_docs):
    content=""
    for item in context_docs:
        content+=item.page_content
        content+="\n"
    return content
#==================================================================================

url="https://youtu.be/j5168Ug7DvA?si=apSbqrG7Zkvk19XGU"
data=fetch_transcrpit(url)

#  SPLITTING INTO CHUNKS
splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
chunks=splitter.split_text(data)

## DEFINING EMBEDDDING MODEL
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",

)

##  DEFINING LLM MODEL
llm = HuggingFacePipeline.from_model_id(
    model_id='TinyLlama/TinyLlama-1.1B-Chat-v1.0',
    task='text-generation',
    pipeline_kwargs=dict(
        temperature=0.5,
        max_new_tokens=100
    )
)
llm = ChatHuggingFace(llm=llm)

## CONVERTING INTO LANGCHAIN DOCUMENTS
docs = [Document(page_content=chunk) for chunk in chunks]

## DEFINING THE VECTORSTORE 
vectorstore=Chroma.from_documents(docs,embedding)


##  DEFINING RETREIVAL 
retriever=vectorstore.as_retriever(search_type="mmr",search_kwargs={"k":2})

##  MAKING PROMPTS
prompt=PromptTemplate(template="""You are a helpful assistant.Answer only from the provided transcript context.If the context is 
in sufficient ,just say you don't know.{context}  , question:{question}""",input_variables=['context','question'])


## MAKING OF CHAIN
parallel_chain=RunnableParallel({
    'context':retriever | RunnableLambda(format_doc),
    'question':RunnablePassthrough()})
parser=StrOutputParser()
final_chain=parallel_chain | prompt | llm | parser

## INFERENCE
ans=final_chain.invoke("what problem is been done in this video")

print(ans)