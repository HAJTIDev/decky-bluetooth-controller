import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import typescript from '@rollup/plugin-typescript';
import replace from '@rollup/plugin-replace';
import css from 'rollup-plugin-import-css';

export default {
  input: 'src/index.tsx',
  output: {
    dir: 'dist',
    format: 'esm',
    exports: 'default',
  },
  plugins: [
    replace({
      'process.env.NODE_ENV': JSON.stringify('production'),
      preventAssignment: true,
    }),
    resolve({
      extensions: ['.js', '.jsx', '.ts', '.tsx']
    }),
    commonjs({
      include: /node_modules/,
    }),
    typescript({
      tsconfig: './tsconfig.json',
    }),
    json(),
    css(),
  ],
  external: ['react', 'react-dom', 'decky-frontend-lib'],
};