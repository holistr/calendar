from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalPermissions, CommentPermissions
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardListSerializer, \
    BoardSerializer


class BoardCreateView(CreateAPIView):
    model = Board
    permission_classes = [IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardListView(ListAPIView):
    model = Board
    permission_classes = [IsAuthenticated, BoardPermissions]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    ordering = ['title']

    def get_queryset(self) -> Board:
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self) -> Board:
        return Board.objects.filter(
            participants__user=self.request.user,
            is_deleted=False
        )

    def perform_destroy(self, instance: Board) -> Board:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'board']

    def get_queryset(self) -> GoalCategory:
        return GoalCategory.objects.filter(
            board__participants__user=self.request.user, is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]

    def get_queryset(self) -> GoalCategory:
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_class = GoalDateFilter
    fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self) -> Goal:
        return Goal.objects.filter(
            category__board__participants__user=self.request.user,
        ).exclude(status=Goal.Status.archived)  # полученный
        # результат исключаем


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self) -> Goal:
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance: Goal) -> Goal:
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, CommentPermissions]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, CommentPermissions]

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)

