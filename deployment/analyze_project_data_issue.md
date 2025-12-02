# 프로젝트 데이터 UI 표시 문제 분석

## 🔍 문제 상황
- DynamoDB에는 프로젝트 데이터가 정상적으로 저장되어 있음 (100개)
- 시작일, 종료일, 팀원 정보가 모두 포함되어 있음
- 하지만 UI에서는 "미정"으로 표시되거나 팀원 수가 제대로 표시되지 않음

## 📊 데이터 흐름 분석

### 1. DynamoDB 저장 구조 (projects_data.json)
```json
{
  "project_id": "PRJ001",
  "project_name": "옴니채널 커머스",
  "status": "completed",
  "period": {
    "start": "2023-12-01",
    "end": "2025-01-24",
    "duration_months": 14
  },
  "team_composition": {
    "Full Stack Developer": ["U_221"],
    "Backend Developer": ["U_052"],
    "Frontend Developer": ["U_045"]
  }
}
```

### 2. Lambda 함수 반환 구조 (index.py)
```python
project = {
    'project_id': item.get('project_id'),
    'project_name': item.get('project_name', ''),
    'status': item.get('status', 'active'),
    'start_date': start_date,        # ✅ period.start에서 추출
    'end_date': end_date,            # ✅ period.end에서 추출
    'duration_months': duration_months,
    'team_members': team_members,    # ✅ team_composition에서 변환
    'team_size': team_size,          # ✅ 팀원 수 계산
    ...
}
```

### 3. 프론트엔드 기대 구조 (ProjectManagement.tsx)
```typescript
const transformedData: Project[] = response.projects.map((proj: APIProject) => {
  return {
    id: proj.project_id,
    name: proj.project_name,
    startDate: proj.start_date || '미정',           // ✅ start_date 사용
    endDate: (proj as any).end_date || '미정',      // ⚠️ end_date를 any로 캐스팅
    assignedMembers: teamMembers.length,            // ⚠️ team_members 길이
    requiredMembers: (proj as any).team_size || 5,  // ⚠️ team_size를 any로 캐스팅
  };
});
```

## ❌ 문제 원인

### 문제 1: TypeScript 타입 정의 불일치
**위치**: `frontend/src/config/api.ts`

Lambda에서 반환하는 필드들이 TypeScript 타입 정의에 포함되지 않아서, 프론트엔드에서 `(proj as any)`로 강제 캐스팅해야 함.

```typescript
// 현재 타입 정의 (추정)
export interface Project {
  project_id: string;
  project_name: string;
  status: string;
  start_date: string;
  required_skills: string[];
  // ❌ end_date, team_size, team_members가 타입에 없음!
}
```

### 문제 2: 데이터 변환 로직 오류
**위치**: `frontend/src/components/ProjectManagement.tsx` 라인 40-65

```typescript
// 현재 코드
const teamMembers = (proj as any).team_members || [];
const assignedMembers = Array.isArray(teamMembers) 
  ? teamMembers.length 
  : ((proj as any).team_size || 0);  // ⚠️ team_members가 배열이 아니면 team_size 사용

// 문제: Lambda에서 team_members를 배열로 반환하지만,
// 타입 정의가 없어서 any로 캐스팅하고 있음
```

### 문제 3: Lambda 함수의 직원 정보 조회 제한
**위치**: `lambda_functions/projects_list/index.py` 라인 119

```python
for user_id in list(all_user_ids)[:50]:  # ⚠️ 최대 50명만 조회
```

프로젝트에 배정된 직원이 50명을 초과하면 일부 직원 정보가 누락됨.

## ✅ 해결 방법

### 해결책 1: TypeScript 타입 정의 수정
`frontend/src/config/api.ts`에 누락된 필드 추가

```typescript
export interface Project {
  project_id: string;
  project_name: string;
  status: string;
  start_date: string;
  end_date: string;              // ✅ 추가
  duration_months: number;       // ✅ 추가
  required_skills: string[];
  team_members: TeamMember[];    // ✅ 추가
  team_size: number;             // ✅ 추가
  client_industry: string;       // ✅ 추가
  budget_scale: string;          // ✅ 추가
  description: string;           // ✅ 추가
}

export interface TeamMember {
  user_id: string;
  name: string;
  role: string;
  employee_role: string;
}
```

### 해결책 2: 프론트엔드 변환 로직 단순화
타입이 정의되면 `as any` 캐스팅 제거 가능

```typescript
const transformedData: Project[] = response.projects.map((proj: APIProject) => {
  return {
    id: proj.project_id,
    name: proj.project_name,
    startDate: proj.start_date || '미정',
    endDate: proj.end_date || '미정',              // ✅ 타입 안전
    assignedMembers: proj.team_members?.length || 0,  // ✅ 타입 안전
    requiredMembers: proj.team_size || 5,         // ✅ 타입 안전
  };
});
```

### 해결책 3: Lambda 직원 조회 최적화
배치 조회 또는 제한 제거

```python
# 옵션 1: 제한 제거 (간단하지만 느릴 수 있음)
for user_id in all_user_ids:

# 옵션 2: DynamoDB BatchGetItem 사용 (권장)
# 최대 100개씩 배치 조회 가능
```

## 🎯 우선순위

1. **즉시 수정 필요**: TypeScript 타입 정의 (api.ts)
2. **즉시 수정 필요**: 프론트엔드 변환 로직 (ProjectManagement.tsx)
3. **성능 개선**: Lambda 직원 조회 최적화 (선택사항)

## 📝 결론

**하드코딩 문제가 아닙니다!**

Lambda 함수는 데이터를 정상적으로 반환하고 있지만, TypeScript 타입 정의가 불완전하여 프론트엔드에서 데이터를 제대로 읽지 못하고 있습니다. 타입 정의만 수정하면 모든 데이터가 정상적으로 표시될 것입니다.
