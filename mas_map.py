import pandas as pd

# CSV 파일 읽기
area_map = pd.read_csv('area_map.csv')
area_struct = pd.read_csv('area_struct.csv')
area_category = pd.read_csv('area_category.csv')

# 각 파일 출력
print("=== area_map.csv ===")
print(area_map)

print("\n=== area_struct.csv ===")
print(area_struct)

print("\n=== area_category.csv ===")
print(area_category)

# area_struct와 area_category를 category 기준으로 병합
struct_with_name = pd.merge(
    area_struct, area_category,
    how="left",
    left_on="category",
    right_on="category"
)

print("\n=== 병합된 구조물 정보 ===")
print(struct_with_name)

# 좌표(x, y)를 기준으로 area_map과 병합
full_map = pd.merge(
    struct_with_name, area_map,
    how="left",
    on=['x', 'y']
)

# area 기준으로 정렬
full_map = full_map.sort_values(by='area')

print("\n=== 전체 병합된 full_map 데이터 ===")
print(full_map)

# area가 1인 데이터만 필터링
area1_data = full_map[full_map['area'] == 1]

print("\n=== area == 1 데이터 ===")
print(area1_data)

# 구조물 이름 비어있는 값 처리 및 건설현장 분류
area1_data['struct'] = area1_data['struct'].fillna('기타')
area1_data.loc[area1_data['ConstructionSite'] == 1, 'struct'] = '건설현장'

# 한글로 구조물 이름 정리
name_map = {
    'Apartment': '아파트',
    'Building': '빌딩',
    'Home': '집',
    'BandalgomCoffee': '반달곰카페',
    '기타': '기타',
    '건설현장': '건설현장'
}
area1_data['struct'] = area1_data['struct'].replace(name_map)

# 구조물 종류별 개수 통계
summary = area1_data['struct'].value_counts().reset_index()
summary.columns = ['구조물 종류', '개수']

print("\n=== 구조물 종류별 요약 통계 리포트 ===")
print(summary)

# CSV 저장
summary.to_csv('structure_summary.csv', index=False)
