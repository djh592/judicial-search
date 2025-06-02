import axios from 'axios';
import {
    CreateQueryRequest,
    CreateQueryResponse,
    QueryResultsResponse,
    QueryMetaResponse,
    UpdateQueryRequest,
    UpdateQueryResponse,
} from './definition';

// 创建查询
export async function createQuery(data: CreateQueryRequest) {
    const resp = await axios.post<CreateQueryResponse>('/api/query', data);
    return resp.data;
}

// 获取查询结果分页
export async function fetchQueryResults(queryId: string, page = 1, pageSize = 10) {
    const resp = await axios.get<QueryResultsResponse>(
        `/api/query/${queryId}/results?page=${page}&page_size=${pageSize}`
    );
    return resp.data;
}

// 获取查询元数据
export async function fetchQueryMeta(queryId: string) {
    const resp = await axios.get<QueryMetaResponse>(`/api/query/${queryId}`);
    return resp.data;
}

// 更新查询
export async function updateQuery(data: UpdateQueryRequest) {
    const resp = await axios.put<UpdateQueryResponse>('/api/query/' + data.query_id, data);
    return resp.data;
}

// 获取文书详情
export async function fetchDocumentDetail(ajid: string) {
    const resp = await axios.get(`/api/document/${ajid}`);
    return resp.data;
}

// 获取所有labels
export async function fetchAllLabels(): Promise<string[]> {
    const resp = await axios.get<{ labels: string[] }>('/api/labels');
    return resp.data.labels;
}

// 搜索补全建议
export async function fetchSuggest(field: string, q: string): Promise<string[]> {
    const resp = await axios.get<{ suggestions: string[] }>('/api/suggest', {
        params: { field, q }
    });
    return resp.data.suggestions;
}