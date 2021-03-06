import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(x_shape=[2, 3, 4, 5], description: str = ""):
    vx = chainer.Variable(np.random.rand(*x_shape).astype(np.float32))
    vy = chainer.functions.log_softmax(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.log_softmax {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test_2d():
    template(x_shape=[5, 10])


def test_3d():
    template(x_shape=[5, 10, 15])


def test_4d():
    template(x_shape=[2, 3, 4, 5])
