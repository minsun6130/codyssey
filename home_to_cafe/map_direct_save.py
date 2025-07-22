import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
from itertools import permutations #보너스 과제 부분


# 지정된 경로에서 csv 파일 불러와 pandas DataFrame으로 반환
def load_map_data(csv_path='sorted_raw_map.csv'):
    return pd.read_csv(csv_path)

# 인수로 데이터 프레임(df), 구조 이름을 받아서 해당 df에서 struct_name인 구조물의 위치만 필터링 
def find_point(df, struct_name):
    df['struct'] = df['struct'].astype(str).str.strip()
    
    point = df[df['struct'] == struct_name] 
    if point.empty:
        raise ValueError(f'{struct_name} 위치를 찾을 수 없습니다.')
    return int(point.iloc[0]['x']), int(point.iloc[0]['y']) #정수 기반 인덱스를 사용해 DataFrame이나 Series의 특정 요소 가져옴


#좌표(nx, ny)가 유효한 이동 위치인지 검사
def is_valid(nx, ny, visited, grid, max_x, max_y):
    return (
        0 <= nx < max_x and
        0 <= ny < max_y and     #격자 x,y 범위 내
        not visited[nx][ny] and #방문한 적 없고
        grid[nx][ny] == 0       #공사구역 아닐 때
    )

#최단거리 알고리즘
def bfs(start, end, grid):
    from_x, from_y = start  #시작 좌표
    to_x, to_y = end        #도착 좌표
    max_x, max_y = len(grid), len(grid[0])
    
    visited = [[False] * max_y for _ in range(max_x)] 
    #전체 격자 방문여부 False로 초기화
    
    prev = [[None] * max_y for _ in range(max_x)] 
    #이전 좌표 저장(경로 추적용), None으로 초기화
    #prev[x][y]는 좌표 (x,y)오기 직전 어디서 왔는지 저장
    
    queue = deque()
    queue.append((from_x, from_y))
    visited[from_x][from_y] = True #BFS 큐 초기화

    while queue:
        x, y = queue.popleft() #큐에서 현재 위치 꺼냄
        if (x, y) == (to_x, to_y): #도착지일 경우 종료
            break

        # 상하좌우 탐색; 유효한 위치면 방문처리, 현재 좌표 저장, 큐에 추가
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny, visited, grid, max_x, max_y):
                visited[nx][ny] = True
                prev[nx][ny] = (x, y)
                queue.append((nx, ny))

    # 역추적 -> 최단 경로 저장 위함
    path = []
    x, y = to_x, to_y
    while (x, y) != (from_x, from_y):
        if prev[x][y] is None:
            return []  # 유효한 경로 없음
        path.append((x, y))
        x, y = prev[x][y]

    path.append((from_x, from_y)) 
    path.reverse()
    return path 
    #시작점 포함 후 순서 뒤집어 최단경로 반환

# 격자 생성하는 함수
def create_grid(df):
    max_x = df['x'].max() + 1
    max_y = df['y'].max() + 1
    grid = [[0] * max_y for _ in range(max_x)]

    for _, row in df.iterrows():
        x, y = int(row['x']), int(row['y'])
        if int(row['ConstructionSite']) == 1:
            grid[x][y] = 1  # constructionsite: 못 지나감
    return grid

# 경로를 데이터 프레임으로 저장하고 home_to_cafe.csv파일로 출력
def save_path_csv(path, filename='home_to_cafe.csv'):
    df = pd.DataFrame(path, columns=['x', 'y'])
    df.to_csv(filename, index=False)

#2단계 지도 그리기 + 빨간선 최단경로 그리기 
def draw_map(df, path, filename='map_final.png'):
    spread_map = df.pivot(index='y', columns='x', values='category')  # x, y 좌표 기반으로 category를 scatter plot로 변환

    legend_names = {1: "Apartment", 2: "Buildings", 3: "My House", 4: "Bandalgom_Cafe", 5: "Construction Site"}  # 카테고리별 이름
    color_map = {1: "saddlebrown", 2: "saddlebrown", 3: "green", 4: "green", 5: "gray"}  # 카테고리별 색상
    marker_map = {1: "o", 2: "o", 3: "^", 4: "s", 5: "s"}  # 카테고리별 모양

    plt.figure(figsize = (6, 6))  # 그래프 크기

    for cat in sorted(df["category"].unique()):
        if cat == 0:
            continue

        subset = df[df["category"] == cat]
        plt.scatter(
            subset["x"], subset["y"],
            c = color_map[cat],
            marker = marker_map[cat],
            label = legend_names[cat],
            edgecolors = 'black',
            s = 400
        )
    
    # 최단 경로 그리기 (빨간 선)
    #유효한 경로가 나오면 빨간 선으로 시각화
    if path: 
        path_x = [x for x, y in path]
        path_y = [y for x, y in path]
        plt.plot(path_x, path_y, c='red', linewidth=2, label='Path')

    # 축 및 기타 시각화 설정
    plt.title("Cafe Map")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend(markerscale=0.6)

    plt.xticks(spread_map.columns)
    plt.yticks(spread_map.index)
    plt.xlim(0.5, 15.5)
    plt.ylim(0.5, 15.5)
    plt.grid(True, linestyle=":", color="black", alpha=1.0)
    plt.gca().invert_yaxis()

    df.to_csv('sorted_raw_map.csv', index=False)  # CSV 저장
    plt.savefig(filename, dpi=300)  # 이미지 저장
    
    print("=== Map saved as '{}' ===".format(filename))
    plt.show()  # 화면에 표시
    plt.close()


#보너스 과제 함수; 모든 구조물(struct: 1~4)를 한 번씩 지나면서 최적 경로를 계산하는 함수
from itertools import permutations

def find_all_struct_path(df):
    """모든 구조물 좌표(카테고리 1~4)를 한 번씩 모두 지나며 최단 경로를 계산"""
    # 구조물 좌표 수집
    struct_df = df[df['category'].isin([1, 2, 3, 4])].copy()
    struct_points = []
    for _, row in struct_df.iterrows(): #struct_df의 각 행 하나씩 꺼냄
        #iterrows(): 데프의 각 행을 하나씩 순회하며 (index, row) 형태로 반환합니다.
        x = int(row['x'])
        y = int(row['y'])               #각 행의 x,y좌표 정수 변환후 튜플로 저장
        struct_points.append((x, y))

    if not struct_points:
        raise ValueError('방문할 구조물이 없습니다.')

    grid = create_grid(df)
    
    # 모든 순열에 대해 전체 경로 계산
    best_path = None
    shortest_len = float('inf')

    for order in permutations(struct_points):
        total_path = []
        valid = True

        for i in range(len(order) - 1):
            segment = bfs(order[i], order[i + 1], grid)
            if not segment:
                valid = False
                break
            if i > 0:
                segment = segment[1:]  # 중복 제거
            total_path.extend(segment)

        if valid and len(total_path) < shortest_len:
            shortest_len = len(total_path)
            best_path = total_path

    if not best_path:
        raise ValueError('구조물을 모두 지나면서 유효한 경로를 찾을 수 없습니다.')

    return best_path



def main():
    df = load_map_data()
    start = find_point(df, 'MyHome')
    end = find_point(df, 'BandalgomCoffee')

    grid = create_grid(df)
    path = bfs(start, end, grid)

    if not path:
        print('경로를 찾을 수 없습니다.')
        return

    save_path_csv(path)
    draw_map(df, path)

    #보너스 과제 
    df = load_map_data()
    path = find_all_struct_path(df)  # 모든 구조물을 통과하는 최단 경로 계산
    save_path_csv(path, 'bonus_home_to_cafe.csv')  # CSV 저장
    draw_map(df, path, 'bonus_map_final.png')  # 시각화


if __name__ == '__main__':
    main()
