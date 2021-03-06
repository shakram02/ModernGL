import struct
import unittest

import ModernGL

from common import get_context


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = get_context()

        cls.vert = cls.ctx.vertex_shader('''
            #version 330

            in vec2 in_v;
            out vec2 out_v;

            uniform Block1 {
                float x;
            };

            uniform Block2 {
                float y;
            };

            uniform Block3 {
                float z;
            };

            void main() {
                out_v = in_v * z + vec2(x, y);
            }
        ''')

        cls.prog = cls.ctx.program(cls.vert, ['out_v'])

    def tearDown(self):
        self.assertEqual(self.ctx.error, 'GL_NO_ERROR')

    def test_1(self):
        buf_v = self.ctx.buffer(struct.pack('2f', 100.0, 1000.0))
        buf_u1 = self.ctx.buffer(struct.pack('f', 9.5))
        buf_u2 = self.ctx.buffer(struct.pack('f', 4.0))
        buf_u3 = self.ctx.buffer(struct.pack('f', 3.0))
        buf_u4 = self.ctx.buffer(struct.pack('f', 0.0))
        buf_r = self.ctx.buffer(reserve=buf_v.size)

        vao = self.ctx.vertex_array(self.prog, [
            (buf_v, '2f', ['in_v']),
        ])

        self.assertFalse('Block1' in self.prog.uniforms)
        self.assertFalse('Block2' in self.prog.uniforms)
        self.assertFalse('Block3' in self.prog.uniforms)

        self.assertFalse('x' in self.prog.uniforms)
        self.assertFalse('y' in self.prog.uniforms)
        self.assertFalse('z' in self.prog.uniforms)

        self.assertTrue('Block1' in self.prog.uniform_blocks)
        self.assertTrue('Block2' in self.prog.uniform_blocks)
        self.assertTrue('Block3' in self.prog.uniform_blocks)

        self.prog.uniform_blocks['Block1'].binding = 2
        self.prog.uniform_blocks['Block2'].binding = 4
        self.prog.uniform_blocks['Block3'].binding = 1

        buf_u1.bind_to_uniform_block(2)
        buf_u2.bind_to_uniform_block(4)
        buf_u4.bind_to_uniform_block(1)

        vao.transform(buf_r)
        a, b = struct.unpack('2f', buf_r.read())
        self.assertAlmostEqual(a, 9.5)
        self.assertAlmostEqual(b, 4.0)

        buf_u3.bind_to_uniform_block(1)

        vao.transform(buf_r)
        a, b = struct.unpack('2f', buf_r.read())
        self.assertAlmostEqual(a, 309.5)
        self.assertAlmostEqual(b, 3004.0)


if __name__ == '__main__':
    unittest.main()
