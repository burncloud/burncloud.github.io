/** User Flow First: sidebar order mirrors runtime execution drill-down, never source directories. */
module.exports = {
  runtimeSidebar: [
    'index',
    {type:'category',label:'API 请求',link:{type:'doc',id:'api-requests/index'},collapsed:false,items:[
      {type:'category',label:'Chat Completion',link:{type:'doc',id:'api-requests/chat-completion/index'},collapsed:false,items:[
        'api-requests/chat-completion/request-entry/index',
        'api-requests/chat-completion/authentication-admission/index',
        'api-requests/chat-completion/model-resolution/index',
        {type:'category',label:'Channel Selection',link:{type:'doc',id:'api-requests/chat-completion/channel-selection/index'},items:[
          'api-requests/chat-completion/channel-selection/candidate-loading/index',
          'api-requests/chat-completion/channel-selection/availability-order-filter/index',
          'api-requests/chat-completion/channel-selection/affinity-ranking/index']},
        {type:'category',label:'Provider Execution',link:{type:'doc',id:'api-requests/chat-completion/provider-execution/index'},items:[
          'api-requests/chat-completion/provider-execution/candidate-attempt-loop/index',
          'api-requests/chat-completion/provider-execution/shaper-circuit-breaker/index',
          'api-requests/chat-completion/provider-execution/protocol-dispatch/index',
          'api-requests/chat-completion/provider-execution/passthrough/index',
          'api-requests/chat-completion/provider-execution/conversion/index',
          'api-requests/chat-completion/provider-execution/failure-retry/index']},
        'api-requests/chat-completion/streaming-response/index',
        'api-requests/chat-completion/billing-settlement/index']},
      'api-requests/video-task-polling/index','api-requests/models/index','api-requests/usage/index']},
    {type:'category',label:'账号访问',link:{type:'doc',id:'account/index'},items:[
      'account/register/index','account/login/index','account/forgot-password/index','account/reset-password/index','account/oauth/index']},
    {type:'category',label:'Console 管理',link:{type:'doc',id:'console/index'},collapsed:false,items:[
      'console/authentication/index',
      {type:'category',label:'Channel 管理',link:{type:'doc',id:'console/channel-management/index'},items:[
        'console/channel-management/list/index','console/channel-management/create/index','console/channel-management/update/index','console/channel-management/get-delete/index']},
      {type:'category',label:'API Token 管理',link:{type:'doc',id:'console/token-management/index'},items:[
        'console/token-management/create/index','console/token-management/rotate/index','console/token-management/manage/index']},
      {type:'category',label:'用户与余额管理',link:{type:'doc',id:'console/user-management/index'},items:[
        'console/user-management/list-users/index','console/user-management/topup/index','console/user-management/recharges/index']},
      'console/logs-usage/index','console/billing-summary/index','console/monitor/index','console/cache/index','console/security/index']},
    {type:'category',label:'内部运维动作',link:{type:'doc',id:'operator/index'},items:[
      'operator/health/index','operator/price-sync/index','operator/circuit-breaker-trip-all/index','operator/metrics/index']}
  ]
};
