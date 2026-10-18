import type { WebRoute } from '@deepseek-ai/dsh-host-webserver';
import { type WorkbenchService } from './service.js';
/**
 * Build the panel API routes.
 * @param service - the workbench host service the routes drive.
 * @returns one exact-match route per endpoint.
 */
export declare function createRoutes(service: WorkbenchService): WebRoute[];
