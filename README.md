# What is this?

This a demo of how to integrate your DAO to the [Taichia DAO Platform](https://www.taichiadao.com). This demo will load the metadata your created on the Chia blockchain recursively. You should be able to use it to initialize your DAO program or do more cool things.

# How to run this?

1. Ensure you installed python3  and have a synced Chia full node.
2. Run this command to install dependencies
>  pip3 install -r requirements.txt
3. copy the .chia/config folder on your full node to overwrite the "config" 
4. If your full node is not on your local host, modify the **self_hostname: &self_hostname "localhost"** in the config.yaml
5. Replace the **DAO_ROOT_PUZHASH** in the metadata_loader.py to your DAO puzzle hash
6. Run this command and your metadata should print out
> python3 metadata_loader.py
# How to integrate this to my DAO?
1. You need to register your DAO on the [Taichia DAO Platform](https://www.taichiadao.com).
2. Create a metadata set for your DAO program and append the metadata puzzle hash to the DAO puzzle hash through our voting service.
3. You need to save the configuration you want to control by voting in the metadata set.
4. Use the code in this demo to load the metadata and plug them into the right place of your DAO program.
