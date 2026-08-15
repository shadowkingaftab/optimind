import { APP_ROUTES } from '../constants/app-routes'

export const ROUTES = {
  ...APP_ROUTES.PUBLIC,
  ...APP_ROUTES.PROTECTED,
  ...APP_ROUTES.ADMIN,
  ...APP_ROUTES.ERROR
} as const

export type RouteKey = keyof typeof ROUTES
