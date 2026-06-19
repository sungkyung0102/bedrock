# AWS Bedrock GitHub PR Review Agent

## 프로젝트 개요

AWS Bedrock Agent와 GitHub API를 활용하여 Pull Request(PR)를 자동으로 분석하고 코드 리뷰 결과를 GitHub 댓글로 등록하는 시스템입니다.

## 시스템 아키텍처

GitHub Pull Request
↓
Bedrock Agent
↓
Action Group
↓
AWS Lambda
↓
GitHub API
↓
PR Comment

## 사용 기술

* Amazon Bedrock Agent
* Amazon Nova Pro
* AWS Lambda
* GitHub REST API
* OpenAPI Schema

## 주요 기능

### 1. Pull Request 조회

GitHub Pull Request의 제목, 설명, 변경 파일 및 Patch 정보를 조회합니다.

### 2. 코드 리뷰 생성

Amazon Nova Pro를 활용하여 코드 품질을 분석하고 개선사항을 제안합니다.

### 3. GitHub 댓글 등록

코드 리뷰 결과를 Pull Request 댓글로 자동 등록합니다.

### 4. 코드 복잡도 분석

조건문 및 반복문을 기준으로 복잡도를 계산합니다.

## 테스트 결과

사용자 요청:

sungkyung0102/bedrock PR 1을 리뷰하고 결과를 댓글로 남겨줘.

결과:

* Pull Request 조회 성공
* 코드 리뷰 생성 성공
* GitHub 댓글 등록 성공

## 프로젝트 회고

* Bedrock Agent와 Action Group 연동 구조를 이해할 수 있었다.
* AWS Lambda와 GitHub API를 활용한 업무 자동화를 구현하였다.
* Amazon Nova Pro를 사용하여 코드 리뷰 기능을 구현하였다.
