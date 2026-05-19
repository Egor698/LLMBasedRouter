from phoenix import otel
from openinference.instrumentation.langchain import LangChainInstrumentor
    
from src.agent.graph import graph
    
def trace():
    trace_provider = otel.register(
        project_name='question-answering-system',
        endpoint='http://localhost:6006/v1/traces',
    )
            
    LangChainInstrumentor().instrument(trace_provider=trace_provider)
    
    
def tracing(question: str):
    trace()
    
    graph.invoke({"question": question})
    
    