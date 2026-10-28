export type MediaType = "video" | "audio" | "image";
export type ContainerType = "mp4" | "mp3" | "jpg" | "png";

export interface MediaFormat {
  format_id: string;
  media_type: MediaType;
  container: ContainerType;
  quality_label: string;
  width?: number | null;
  height?: number | null;
  estimated_size_bytes?: number | null;
  requires_conversion: boolean;
  note?: string | null;
}

export interface MediaMetadata {
  title: string;
  creator?: string | null;
  thumbnail_url?: string | null;
  duration_seconds?: number | null;
  source_url: string;
}

export interface AnalyzeResponse {
  analysis_id: string;
  platform: string;
  content_type: string;
  metadata: MediaMetadata;
  formats: MediaFormat[];
  warnings: string[];
}

export type JobStatus =
  | "queued"
  | "downloading"
  | "converting"
  | "completed"
  | "failed"
  | "cancelled";

export interface DownloadJobResponse {
  job_id: string;
  status: JobStatus;
  events_url: string;
  download_url?: string | null;
  percent?: number | null;
  message?: string | null;
  filename?: string | null;
  file_size?: number | null;
}

export interface PlatformCapability {
  id: string;
  name: string;
  hostname_patterns: string[];
  supported_content_types: string[];
  supported_formats: string[];
  enabled: boolean;
  policy_notice: string;
}

export interface PlatformListResponse {
  platforms: PlatformCapability[];
  legal_disclaimer: string;
}

export type UXState =
  | "idle"
  | "validating"
  | "analyzing"
  | "complete"
  | "no_formats"
  | "format_selected"
  | "preparing"
  | "downloading"
  | "completed"
  | "failed"
  | "cancelled";

