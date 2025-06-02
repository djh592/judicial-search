// 用户查询参数
export interface UserQuery {
    query?: string;
    qw?: string;
    ajmc?: string;
    ay?: string;
    fymc?: string;
    spry?: string;
    dsr?: string;
}

// 创建查询请求体
export interface CreateQueryRequest {
    user_query: UserQuery;
}

// 创建查询响应
export interface CreateQueryResponse {
    query_id: string;
    total_results: number;
}

// 查询结果单条
export interface CaseResult {
    ajid: string;
    ajName: string;
    ajjbqk: string;
    cpfxgc: string;
    pjjg: string;
    qw: string;
    writId: string;
    writName: string;
    [key: string]: any;
}

// 查询结果分页响应
export interface QueryResultsResponse {
    page: number;
    total_pages: number;
    results: CaseResult[];
}

// 查询元数据响应
export interface QueryMetaResponse {
    id: string;
    params: UserQuery;
    created_at: number;
    last_accessed: number;
    total_results: number;
    version: number;
}

// 更新查询请求体
export interface UpdateQueryRequest {
    query_id: string;
    user_query: UserQuery;
}

// 更新查询响应
export interface UpdateQueryResponse {
    query_id: string;
    total_results: number;
}