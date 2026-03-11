// TypeScript interfaces matching backend Pydantic schemas

// ─── Enums ───────────────────────────────────────────────────────────────────

export type CaseStatus = 'active' | 'observing' | 'closed' | 'resolved' | 'archived'

export type CredibilityLevel = 'high' | 'medium' | 'low' | 'unverified'

export type SourceType =
    | 'government'
    | 'mainstream_media'
    | 'academic'
    | 'local_media'
    | 'social_media'
    | 'unknown'

export type FeedType = 'rss' | 'api' | 'scraper'

export type FeedStatus = 'normal' | 'warning' | 'offline' | 'paused'

// ─── Common ──────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
    total: number
    page: number
    page_size: number
    items: T[]
}

export interface ErrorResponse {
    detail: string
}

// ─── Tag ─────────────────────────────────────────────────────────────────────

export interface TagOut {
    id: string
    name: string
}

export interface TagWithCount extends TagOut {
    case_count: number
}

// ─── Case ────────────────────────────────────────────────────────────────────

export interface CaseSummary {
    id: string
    title: string
    status: CaseStatus
    hotness_score: number
    tags: TagOut[]
    event_count: number
    source_count: number
    created_at: string
    last_event_at: string | null
}

export interface CaseDetail extends CaseSummary {
    description: string | null
}

export interface CaseCreate {
    title: string
    description?: string
    tag_ids?: string[]
}

export interface CaseUpdate {
    title?: string
    description?: string
    status?: CaseStatus
    tag_ids?: string[]
}

export interface SearchSuggestedCase {
    id: string
    title: string
    status: CaseStatus
    event_count: number
}

// ─── EventNode ───────────────────────────────────────────────────────────────

export interface CredibilityBrief {
    level: CredibilityLevel
    total_score: number
    has_conflict: boolean
}

export interface EventSummary {
    id: string
    title: string
    event_time: string
    source_count: number
    credibility: CredibilityBrief | null
    sources: SourceBrief[]
}

export interface SourceBrief {
    id: string
    name: string
    source_type: SourceType
    url: string
    reputation_score: number
    has_false_history: boolean
    collected_at: string
}

export interface EventDetail extends EventSummary {
    case_id: string
    summary: string | null
    sources: SourceBrief[]
}

// ─── Credibility ─────────────────────────────────────────────────────────────

export interface ScoringExplanation {
    authority: string
    timeliness: string
    cross_verify: string
}

export interface SourceWithCredibility {
    source_id: string
    source_name: string
    source_type: string
    url: string
    reputation_score: number
    has_false_history: boolean
    authority_contribution: number
    is_accessible: boolean
    collected_at: string
    warnings: string[]
}

export interface CredibilityDetail {
    event_id: string
    event_title: string
    level: CredibilityLevel
    total_score: number
    authority_score: number
    timeliness_score: number
    cross_verify_score: number
    source_count: number
    has_conflict: boolean
    conflict_sources: string[]
    sources: SourceWithCredibility[]
    scoring_explanation: ScoringExplanation | null
    assessed_at: string
}

export interface CredibilityOverall {
    event_id: string
    level: CredibilityLevel
    total_score: number
    has_conflict: boolean
    conflict_sources: string[]
    detail: CredibilityDetail
}

// ─── DataFeed ────────────────────────────────────────────────────────────────

export interface DataFeedOut {
    id: string
    name: string
    feed_type: FeedType
    url: string
    status: FeedStatus
    consecutive_failures: number
    last_collected_at: string | null
    schedule_cron: string
    created_at: string
    is_builtin: boolean
}

export interface DataFeedCreate {
    name: string
    feed_type: FeedType
    url: string
    schedule_cron?: string
    parse_config?: Record<string, unknown>
}

export interface DataFeedUpdate {
    name?: string
    url?: string
    schedule_cron?: string
    status?: FeedStatus
    parse_config?: Record<string, unknown>
}

export interface CollectTriggerResponse {
    feed_id: string
    message: string
    triggered_at: string
    status: string
}
