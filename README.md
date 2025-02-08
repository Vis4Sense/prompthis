# PrompTHis

A visual anlaytics system for exploring prompt history when using text-to-image generative models ([online demo](https://vis4sense.github.io/prompthis), [paper](https://doi.org/10.1109/TVCG.2024.3408255)).

## Architecture

[Client](./client/) and [server](./server/) construct the web interface. [Diffusion](./diffusion/) and [preprocess](./preprocess/) generate, log, and preprocess images.

![Architecture](./assets/architecture.png)

## Usage

Currently, the backends ([diffusion](./diffusion/), [preprocess](./preprocess/), and [server](./server/)) are hosted at <https://vis.pku.edu.cn/prompthis>. The host is sometimes inaccessible due to domain restrictions. Details on setting up the backends locally are coming soon.

To use the front end,

1. `cd client`
2. Run `npm install` to install dependencies
3. Run `npm run dev` to launch the dev server

## Reference

```bibTeX
@article{guo2024prompthis,
  author={Guo, Yuhan and Shao, Hanning and Liu, Can and Xu, Kai and Yuan, Xiaoru},
  journal={IEEE Transactions on Visualization and Computer Graphics}, 
  title={PrompTHis: Visualizing the Process and Influence of Prompt Editing during Text-to-Image Creation}, 
  year={2024},
  doi={10.1109/TVCG.2024.3408255}
}
```
