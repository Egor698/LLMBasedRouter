from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

from langgraph.graph import StateGraph, START, END

from src.agent.schemes import SClassification, SAnswer
from src.data.context import classifications_contexts
from src.data.prompts import CLASSIFICATION_PROMPT, ANSWER_PROMPT

class State(TypedDict):
    question: str
    classifications: list[Literal[1, 2, 3, 4, 5]]
    full_context: str
    assured_answer: bool
    answer: str
    

llm = ChatOpenAI(base_url='https://gatellm.ru/v1',
                              api_key='sk-de3a41995e9714daefc75c77f027979445e1dbbd1bf8632c93981b4ed96acc9d',
                              model='openai/gpt-4o-mini',
                              temperature=0.4)


def llm_give_question_classifications(state: State) -> State:
    prompt_template = PromptTemplate.from_template(CLASSIFICATION_PROMPT)
    
    prepared_llm = llm.with_structured_output(SClassification)
    
    chain = prompt_template | prepared_llm
    
    answer = chain.invoke({'question': state['question']})

    return {'classifications': answer.classifications}


def call_moderator(state: State) -> State:
    print(f"""Вопрос требует ручной модерации.
          Вопрос: {state['question']}
          Предварительный ответ AI: {state.get('answer', 'Нет данных')}
          Контекст: {state.get('full_context', 'Нет данных')}
          """)
    
    return {'assured_answer': False}
    
    
def route_by_classifications(state: State) -> State:
    if len(state['classifications']) == 1 and state['classifications'][0] == 5:
        return 'call_moderator'
    
    return 'enrich_context'


def enrich_context(state: State) -> State:
    context = []
    
    for classification in state['classifications']:
        if classification in classifications_contexts:
            context.append(classifications_contexts[classification])

    return {'full_context': '\n'.join(context)}


def llm_try_answer(state: State) -> State:
    prompt_template = PromptTemplate.from_template(ANSWER_PROMPT)
    
    prepared_llm = llm.with_structured_output(SAnswer)
    
    chain = prompt_template | prepared_llm
    
    answer = chain.invoke({'question': state['question'], 'full_context': state['full_context']})
    
    return {'assured_answer': answer.assured_answer, 'answer': answer.answer}
    
    
def route_to_moderator_or_answer(state: State) -> State:
    if not state['assured_answer']:
        return 'call_moderator'
    
    return '__end__'


builder = StateGraph(State)


builder.add_node('llm_give_question_classifications', llm_give_question_classifications)
builder.add_node('call_moderator', call_moderator)
builder.add_node('enrich_context', enrich_context)
builder.add_node('llm_try_answer', llm_try_answer)


builder.add_edge(START, 'llm_give_question_classifications')
builder.add_conditional_edges('llm_give_question_classifications',
                              route_by_classifications,
                              {'call_moderator': 'call_moderator', 
                               'enrich_context': 'enrich_context'})


builder.add_edge('enrich_context', 'llm_try_answer')
builder.add_conditional_edges('llm_try_answer',
                              route_to_moderator_or_answer,
                              {'call_moderator': 'call_moderator', 
                              '__end__': END})


builder.add_edge('call_moderator', END)


graph = builder.compile()


