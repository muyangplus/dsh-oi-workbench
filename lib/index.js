/**
 * dsh-oi-workbench — OI 出题工作台（DeepSeek Harness skill-only plugin）。
 *
 * 本包为纯 skill 插件：通过 cordis.patch.yml 在 host 组合中注册一个
 * `@deepseek-ai/dsh-skill-filesystem` 提供方（providerName: oi-workbench-plugin），
 * 把包内 `skills/oi-workbench/` 暴露为可加载的 skill。
 * 无需任何运行时逻辑；本入口仅用于包解析辅助。
 */
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';

export const name = 'dsh-oi-workbench';
export const PACKAGE_NAME = 'dsh-oi-workbench';

export function resolveOiWorkbenchSkillRoot(profileBaseUrl) {
  if (!profileBaseUrl) {
    throw new Error('dsh-oi-workbench: missing DSH profile baseUrl for package resolution');
  }
  let manifestPath;
  try {
    manifestPath = createRequire(profileBaseUrl).resolve(`${PACKAGE_NAME}/package.json`);
  } catch (error) {
    throw new Error(
      `dsh-oi-workbench: cannot resolve ${PACKAGE_NAME}/package.json from the DSH profile`,
      { cause: error },
    );
  }
  return join(dirname(manifestPath), 'skills');
}
