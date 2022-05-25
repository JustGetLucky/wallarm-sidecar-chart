{{/*
Expand the name of the chart.
*/}}

{{- define "wallarm-sidecar.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "wallarm-sidecar.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "wallarm-sidecar.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "wallarm-sidecar.labels" -}}
helm.sh/chart: {{ include "wallarm-sidecar.chart" . }}
{{ include "wallarm-sidecar.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ template "wallarm-sidecar.name" . }}
{{- if .Values.commonLabels }}
{{ toYaml .Values.commonLabels }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "wallarm-sidecar.selectorLabels" -}}
app.kubernetes.io/name: {{ include "wallarm-sidecar.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{- define "wallarm-sidecar.postanalytics.name" -}}{{ include "wallarm-sidecar.name" . }}-postanalytics{{- end -}}
{{- define "wallarm-sidecar.postanalytics.secret" -}}{{ include "wallarm-sidecar.name" . }}-postanalytics-secret{{- end -}}
{{- define "wallarm-sidecar.postanalytics.tarantoolPort" -}}3313{{- end -}}
{{- define "wallarm-sidecar.postanalytics.cronConfig" -}}{{ include "wallarm-sidecar.name" . }}-postanalytics-cron{{- end -}}

{{- define "wallarm-sidecar.postanalytics.containerSecurityContext" -}}
{{- if .Values.postanalytics.containerSecurityContext -}}
{{- toYaml .Values.postanalytics.containerSecurityContext -}}
{{- else -}}
capabilities:
  drop:
  - ALL
  add:
  - NET_BIND_SERVICE
runAsUser: {{ .Values.postanalytics.runAsUser }}
allowPrivilegeEscalation: {{ .Values.postanalytics.allowPrivilegeEscalation }}
{{- end }}
{{- end -}}

{{- define "wallarm-sidecar.postanalytics.wallarmApiEnv" -}}
- name: WALLARM_API_HOST
  value: {{ .Values.wallarmApi.host | default "api.wallarm.com" }}
- name: WALLARM_API_PORT
  value: {{ .Values.wallarmApi.port | default "444" | quote }}
- name: WALLARM_API_USE_SSL
  value: {{ .Values.wallarmApi.useSSL | toString | quote }}
- name: WALLARM_API_CA_VERIFY
  value: {{ .Values.wallarmApi.caVerify | toString | quote }}
- name: WALLARM_API_TOKEN
  valueFrom:
    secretKeyRef:
      key: token
      name: {{ template "wallarm-sidecar.postanalytics.secret" . }}
{{- end -}}