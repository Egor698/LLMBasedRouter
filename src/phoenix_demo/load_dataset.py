import phoenix.client as px_client

client = px_client.Client(base_url='http://localhost:6006')

def load_dataset():

    dataset = client.datasets.create_dataset(name=...,
                                            dataset_description=...,
                                            dataframe=...,
                                            input_keys=['input'],
                                            output_keys=['expected_output'],
                                            metadata_keys=['context'],
                                            )
    
    return dataset

