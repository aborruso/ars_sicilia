import path from 'node:path';

export default function remarkDefaultLayout(options = {}) {
  const { layout } = options;
  const layoutPath = layout ? path.resolve(process.cwd(), layout) : null;

  return (_tree, file) => {
    if (!layoutPath) {
      return;
    }

    if (!file.data.astro) {
      file.data.astro = {};
    }

    if (!file.data.astro.frontmatter) {
      file.data.astro.frontmatter = {};
    }

    if (!file.data.astro.frontmatter.layout && file.path) {
      const relativePath = path.relative(path.dirname(file.path), layoutPath);
      file.data.astro.frontmatter.layout = relativePath.startsWith('.')
        ? relativePath
        : `./${relativePath}`;
    }
  };
}
