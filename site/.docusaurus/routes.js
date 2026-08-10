import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/',
    component: ComponentCreator('/', '687'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', '31b'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', '985'),
            routes: [
              {
                path: '/account/',
                component: ComponentCreator('/account/', '901'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/account/forgot-password/',
                component: ComponentCreator('/account/forgot-password/', '56b'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/account/login/',
                component: ComponentCreator('/account/login/', '353'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/account/oauth/',
                component: ComponentCreator('/account/oauth/', 'dd4'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/account/register/',
                component: ComponentCreator('/account/register/', '7c2'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/account/reset-password/',
                component: ComponentCreator('/account/reset-password/', '676'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/',
                component: ComponentCreator('/api-requests/', '7d3'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/',
                component: ComponentCreator('/api-requests/chat-completion/', '709'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/authentication-admission/',
                component: ComponentCreator('/api-requests/chat-completion/authentication-admission/', '49f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/billing-settlement/',
                component: ComponentCreator('/api-requests/chat-completion/billing-settlement/', 'e30'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/channel-selection/',
                component: ComponentCreator('/api-requests/chat-completion/channel-selection/', 'adc'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/channel-selection/affinity-ranking/',
                component: ComponentCreator('/api-requests/chat-completion/channel-selection/affinity-ranking/', 'b4d'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/channel-selection/availability-order-filter/',
                component: ComponentCreator('/api-requests/chat-completion/channel-selection/availability-order-filter/', 'dc1'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/channel-selection/candidate-loading/',
                component: ComponentCreator('/api-requests/chat-completion/channel-selection/candidate-loading/', '8c5'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/model-resolution/',
                component: ComponentCreator('/api-requests/chat-completion/model-resolution/', '87b'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/', '404'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/candidate-attempt-loop/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/candidate-attempt-loop/', 'b1f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/conversion/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/conversion/', 'c7d'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/failure-retry/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/failure-retry/', '374'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/passthrough/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/passthrough/', 'f13'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/protocol-dispatch/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/protocol-dispatch/', '1b2'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/',
                component: ComponentCreator('/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/', 'ea7'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/request-entry/',
                component: ComponentCreator('/api-requests/chat-completion/request-entry/', '7eb'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/chat-completion/streaming-response/',
                component: ComponentCreator('/api-requests/chat-completion/streaming-response/', '823'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/models/',
                component: ComponentCreator('/api-requests/models/', '62f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/usage/',
                component: ComponentCreator('/api-requests/usage/', '6d5'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/api-requests/video-task-polling/',
                component: ComponentCreator('/api-requests/video-task-polling/', 'f63'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/',
                component: ComponentCreator('/console/', 'd49'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/authentication/',
                component: ComponentCreator('/console/authentication/', 'd30'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/billing-summary/',
                component: ComponentCreator('/console/billing-summary/', 'e0b'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/cache/',
                component: ComponentCreator('/console/cache/', '3db'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/channel-management/',
                component: ComponentCreator('/console/channel-management/', '351'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/channel-management/create/',
                component: ComponentCreator('/console/channel-management/create/', '59f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/channel-management/get-delete/',
                component: ComponentCreator('/console/channel-management/get-delete/', 'a7b'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/channel-management/list/',
                component: ComponentCreator('/console/channel-management/list/', '168'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/channel-management/update/',
                component: ComponentCreator('/console/channel-management/update/', '862'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/logs-usage/',
                component: ComponentCreator('/console/logs-usage/', 'c9a'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/monitor/',
                component: ComponentCreator('/console/monitor/', 'de1'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/security/',
                component: ComponentCreator('/console/security/', '6c6'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/token-management/',
                component: ComponentCreator('/console/token-management/', 'e07'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/token-management/create/',
                component: ComponentCreator('/console/token-management/create/', 'f6a'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/token-management/manage/',
                component: ComponentCreator('/console/token-management/manage/', 'fd0'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/token-management/rotate/',
                component: ComponentCreator('/console/token-management/rotate/', '814'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/user-management/',
                component: ComponentCreator('/console/user-management/', 'ccf'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/user-management/list-users/',
                component: ComponentCreator('/console/user-management/list-users/', '26f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/user-management/recharges/',
                component: ComponentCreator('/console/user-management/recharges/', '36f'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/console/user-management/topup/',
                component: ComponentCreator('/console/user-management/topup/', 'c1d'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/operator/',
                component: ComponentCreator('/operator/', '501'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/operator/circuit-breaker-trip-all/',
                component: ComponentCreator('/operator/circuit-breaker-trip-all/', '71e'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/operator/health/',
                component: ComponentCreator('/operator/health/', 'db1'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/operator/metrics/',
                component: ComponentCreator('/operator/metrics/', 'c61'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/operator/price-sync/',
                component: ComponentCreator('/operator/price-sync/', '798'),
                exact: true,
                sidebar: "runtimeSidebar"
              },
              {
                path: '/',
                component: ComponentCreator('/', '9bc'),
                exact: true,
                sidebar: "runtimeSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
