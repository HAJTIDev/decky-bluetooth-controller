import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import typescript from '@rollup/plugin-typescript';
import css from 'rollup-plugin-import-css';

export default {
  input: 'src/index.tsx',
  output: {
    dir: 'dist',
    format: 'cjs',
  },
  plugins: [
    resolve(),
    commonjs(),
    json(),
    typescript(),
    css(),
  ],
  external: ['react', 'react-dom'],
};