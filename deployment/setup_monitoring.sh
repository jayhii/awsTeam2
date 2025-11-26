#!/bin/bash

# HR Resource Optimization System - 모니터링 설정 스크립트
# 이 스크립트는 CloudWatch 대시보드와 알람을 확인하고 SNS 구독을 설정합니다.

set -e

echo "=========================================="
echo "HR Resource Optimization - 모니터링 설정"
echo "=========================================="
echo ""

# Terraform 디렉토리로 이동
cd "$(dirname "$0")/terraform"

# Terraform outputs 확인
echo "1. CloudWatch 대시보드 확인 중..."
DASHBOARDS=$(terraform output -json cloudwatch_dashboards 2>/dev/null || echo "{}")

if [ "$DASHBOARDS" != "{}" ]; then
    echo "✓ 생성된 대시보드:"
    echo "$DASHBOARDS" | jq -r 'to_entries[] | "  - \(.key): \(.value)"'
    echo ""
    echo "AWS Console에서 확인:"
    echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:"
else
    echo "✗ 대시보드를 찾을 수 없습니다. Terraform apply를 먼저 실행하세요."
    exit 1
fi

echo ""
echo "2. SNS Topic 확인 중..."
SNS_TOPIC_ARN=$(terraform output -raw sns_topic_arn 2>/dev/null || echo "")

if [ -n "$SNS_TOPIC_ARN" ]; then
    echo "✓ SNS Topic ARN: $SNS_TOPIC_ARN"
    
    # 구독 목록 확인
    echo ""
    echo "3. 현재 SNS 구독 확인 중..."
    SUBSCRIPTIONS=$(aws sns list-subscriptions-by-topic --topic-arn "$SNS_TOPIC_ARN" --query 'Subscriptions[*].[Protocol,Endpoint,SubscriptionArn]' --output table 2>/dev/null || echo "")
    
    if [ -n "$SUBSCRIPTIONS" ]; then
        echo "$SUBSCRIPTIONS"
    else
        echo "  현재 구독이 없습니다."
    fi
    
    # 이메일 구독 추가 옵션
    echo ""
    read -p "이메일 알림을 추가하시겠습니까? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "이메일 주소를 입력하세요: " EMAIL
        
        if [ -n "$EMAIL" ]; then
            echo "이메일 구독 추가 중..."
            aws sns subscribe \
                --topic-arn "$SNS_TOPIC_ARN" \
                --protocol email \
                --notification-endpoint "$EMAIL"
            
            echo "✓ 구독 요청이 전송되었습니다."
            echo "  $EMAIL 로 전송된 확인 이메일의 링크를 클릭하세요."
        fi
    fi
else
    echo "✗ SNS Topic을 찾을 수 없습니다."
fi

echo ""
echo "4. CloudWatch 알람 확인 중..."
ALARMS=$(aws cloudwatch describe-alarms --alarm-name-prefix "lambda-errors" --query 'MetricAlarms[*].[AlarmName,StateValue]' --output table 2>/dev/null || echo "")

if [ -n "$ALARMS" ]; then
    echo "$ALARMS"
else
    echo "  알람을 찾을 수 없습니다."
fi

echo ""
echo "=========================================="
echo "모니터링 설정 완료"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. AWS Console에서 CloudWatch 대시보드 확인"
echo "2. 이메일 구독 확인 링크 클릭 (구독 추가한 경우)"
echo "3. 알람 테스트 수행"
echo ""
echo "대시보드 URL:"
echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:"
echo ""
echo "알람 URL:"
echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#alarmsV2:"
echo ""

