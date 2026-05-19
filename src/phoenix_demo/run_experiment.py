from phoenix.client import Client
from phoenix.client.experiments import create_evaluator, run_experiment

from src.agent.graph import graph
from src.phoenix_demo.tracing import trace

client = Client(base_url='http://localhost:6006')

def task(input) -> dict:
    output = graph.invoke({'question': input['input']})
    return output


@create_evaluator(name='assured_answer_accuracy', kind='CODE')
def evaluate_assured_answer_accuracy(output: dict, example):
    exemple_output = example.output
    
    if output['assured_answer'] is exemple_output['assured_answer']:
        return 1
    else:
        return 0
    
    
@create_evaluator(name='classification_accuracy', kind='CODE')
def evaluator_classifications_accuracy(output: dict, example) -> float:
    exemple_output = example.output
    
    suf_count = len([x for x in exemple_output['classifications']
                    if x in output['classifications']])
    
    return suf_count / len(exemple_output['classifications'])


def go_experiment():
    trace()
    
    dataset = client.datasets.get_dataset(dataset='benchmark')

    run_experiment(
        experiment_name='base_testing',
        dataset=dataset,
        task=task,
        evaluators=[evaluate_assured_answer_accuracy, evaluator_classifications_accuracy]
    )
    
go_experiment()